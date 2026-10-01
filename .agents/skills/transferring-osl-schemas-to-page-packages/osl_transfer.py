"""Transfer OSL page files from an application repo into OSW page package submodules.

Package files are named by page (``<OSW-ID>.slot_<slot>`` or ``<Name>.slot_<slot>``). The
source naming differs per repository and is given with ``--suffix`` (source suffix to
package suffix, one per file kind) and ``--name-prefix`` (stems of pages named by the
jsondata ``name``, usually Property pages), for example:

  map --src <dir> --suffix .jsondata.json=slot_jsondata.json --name-prefix Property_=Property

This tool maps one to the other, compares parsed content against a git ref, and writes
merged package files that keep the target file format and the ref key order.

Subcommands (run ``<subcommand> --help`` for options):
  map      list source pages and their package files (read-only)
  compare  compare source files with the package files at a git ref (read-only)
  merge    write source content into the package working tree
  drop     remove a key or list item from any JSON file, keeping its format

Key paths are dot separated. A list item is selected by one of its fields:
``properties.name.description`` or ``items_list[id=example.org]``.
Merge options take ``<Stem>.<kind>:<path>``, where kind is the package slot name
between ``slot_`` and the first dot, for example jsondata or jsonschema.
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys

# Format used by the package files when no target file exists yet
PACKAGE_FORMAT = {
    "indent": 4,
    "newline": "\r\n",
    "final_newline": False,
    "ensure_ascii": False,
}
PACKAGE_SUFFIX = re.compile(r"^slot_(?P<kind>[A-Za-z0-9_]+)\.[A-Za-z0-9]+$")
SEG = re.compile(r"^(?P<key>[^\[]+)(\[(?P<field>[^=\]]+)=(?P<value>[^\]]*)\])?$")


def default_packages():
    # the git toplevel does not depend on how deep this script is in the repository
    r = git(pathlib.Path(__file__).resolve().parent, "rev-parse", "--show-toplevel")
    root = (
        pathlib.Path(r.stdout.decode().strip())
        if r.returncode == 0
        else pathlib.Path.cwd()
    )
    return root / "packages"


def _pairs(values, option):
    out = {}
    for v in values or []:
        left, _, right = v.partition("=")
        if not left or not right:
            raise SystemExit(f"{option} expects <left>=<right>, got {v!r}")
        out[left] = right
    return out


def suffix_map(values):
    """Return {source suffix: package suffix} from ``--suffix`` values."""
    suffixes = _pairs(values, "--suffix")
    for s, t in suffixes.items():
        if not PACKAGE_SUFFIX.match(t):
            raise SystemExit(
                f"--suffix {s}={t}: the package suffix must look like slot_<slot>.<ext>"
            )
    if list(suffixes.values()).count("slot_jsondata.json") != 1:
        raise SystemExit(
            "exactly one --suffix must map to slot_jsondata.json, the page is derived from that file"
        )
    return suffixes


def kind(package_suffix):
    return PACKAGE_SUFFIX.match(package_suffix)["kind"]


# --- source discovery -------------------------------------------------------


def source_pages(src, suffixes):
    """Return {stem: {suffix: path}} for all known source files in ``src``."""
    pages = {}
    for f in sorted(src.iterdir()):
        # a file belongs to its longest matching suffix only, e.g. .jsondata.json before .json
        matches = sorted((s for s in suffixes if f.name.endswith(s)), key=len)
        if matches:
            pages.setdefault(f.name[: -len(matches[-1])], {})[matches[-1]] = f
    return pages


def page_file_base(stem, jsondata_file, prefixes):
    """Return (namespace, package file base name without ``.slot_*``) of a source page."""
    jd = json.loads(read_raw(jsondata_file))
    matches = sorted((p for p in prefixes if stem.startswith(p)), key=len)
    if matches:
        return prefixes[matches[-1]], jd["name"]
    return "Category/Item", "OSW" + jd["uuid"].replace("-", "")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True)


def find_target(packages, base, ref):
    """Return (package_dir, relative base path) of a page, searching the working tree, then ``ref``."""
    hits = [
        (h.parents[2], h.relative_to(h.parents[2]).as_posix())
        for h in sorted(packages.glob(f"*/*/*/{base}.slot_jsondata.json"))
    ]
    if not hits:
        for pkg in sorted(p for p in packages.iterdir() if (p / ".git").exists()):
            names = (
                git(pkg, "ls-tree", "-r", "--name-only", ref)
                .stdout.decode()
                .splitlines()
            )
            hits += [
                (pkg, n) for n in names if n.endswith(f"/{base}.slot_jsondata.json")
            ]
    if len(hits) > 1:
        raise SystemExit(
            f"{base} exists in more than one package: "
            + ", ".join(f"{p.name}/{n}" for p, n in hits)
        )
    if hits:
        pkg, name = hits[0]
        return pkg, name[: -len(".slot_jsondata.json")]
    return None, None


def resolve(args):
    """Yield (stem, suffix, source file, package dir, target relative path) for selected pages."""
    suffixes = suffix_map(args.suffix)
    prefixes = _pairs(args.name_prefix, "--name-prefix")
    jsondata_suffix = next(s for s, t in suffixes.items() if t == "slot_jsondata.json")
    pages = source_pages(pathlib.Path(args.src), suffixes)
    wanted = set(args.pages or pages)
    for missing in sorted(wanted - set(pages)):
        print(f"ERROR {missing}: no source files", file=sys.stderr)
    for stem in sorted(wanted & set(pages)):
        files = pages[stem]
        if jsondata_suffix not in files:
            print(
                f"SKIP {stem}: no jsondata file, cannot derive the page",
                file=sys.stderr,
            )
            continue
        namespace, base = page_file_base(stem, files[jsondata_suffix], prefixes)
        pkg, rel = find_target(pathlib.Path(args.packages), base, args.ref)
        for suffix, f in files.items():
            yield stem, suffixes[suffix], f, pkg, (
                f"{rel}.{suffixes[suffix]}" if rel else f"{namespace}:{base}"
            )


# --- json helpers -----------------------------------------------------------


def split_path(path):
    segs = []
    # split at dots outside of [...], since selector values can contain dots
    for s in re.findall(r"(?:[^.\[]|\[[^\]]*\])+", path):
        m = SEG.match(s)
        if not m:
            raise SystemExit(f"invalid key path segment: {s!r}")
        segs.append(m.groupdict())
    return segs


def _step(obj, seg, create=False):
    obj = obj[seg["key"]] if not create else obj.setdefault(seg["key"], {})
    if seg["field"]:
        matches = [
            i
            for i in obj
            if isinstance(i, dict) and str(i.get(seg["field"])) == seg["value"]
        ]
        if len(matches) != 1:
            raise KeyError(
                f"{seg['key']}[{seg['field']}={seg['value']}] matched {len(matches)} items"
            )
        obj = matches[0]
    return obj


def get_path(obj, path):
    for seg in split_path(path):
        obj = _step(obj, seg)
    return obj


def set_path(obj, path, value):
    *parents, last = split_path(path)
    for seg in parents:
        obj = _step(obj, seg)
    if last["field"]:
        # keep one list item: replace the item with the same field value, or append it
        items = obj.setdefault(last["key"], [])
        same = [
            i
            for i, it in enumerate(items)
            if isinstance(it, dict) and str(it.get(last["field"])) == last["value"]
        ]
        if same:
            items[same[0]] = value
        else:
            items.append(value)
        return
    obj[last["key"]] = value


def delete_path(obj, path):
    *parents, last = split_path(path)
    for seg in parents:
        obj = _step(obj, seg)
    if last["field"]:
        item = _step(obj, last)
        obj[last["key"]].remove(item)
    else:
        del obj[last["key"]]


def diff_paths(new, ref, prefix=""):
    """List differences as ``L path`` (only new), ``M path`` (only ref), ``~ path`` (changed)."""
    out = []
    if isinstance(new, dict) and isinstance(ref, dict):
        for k in list(new) + [k for k in ref if k not in new]:
            p = f"{prefix}{k}"
            if k not in ref:
                out.append(f"L {p}")
            elif k not in new:
                out.append(f"M {p}")
            elif new[k] != ref[k]:
                out += diff_paths(new[k], ref[k], p + ".")
    elif _id_list(new) and _id_list(ref):
        base = prefix.rstrip(".")
        by_ref = {i["id"]: i for i in ref}
        by_new = {i["id"]: i for i in new}
        for i, item in by_new.items():
            if i not in by_ref:
                out.append(f"L {base}[id={i}]")
            elif item != by_ref[i]:
                out += diff_paths(item, by_ref[i], f"{base}[id={i}].")
        out += [f"M {base}[id={i}]" for i in by_ref if i not in by_new]
        if not out and new != ref:
            out.append(f"~ {base} (order)")
    elif _scalar_list(new) and _scalar_list(ref):
        base = prefix.rstrip(".")
        out += [f"L {base} (item {json.dumps(i)})" for i in new if i not in ref]
        out += [f"M {base} (item {json.dumps(i)})" for i in ref if i not in new]
        if not out:
            out.append(f"~ {base} (order)")
    else:
        out.append(f"~ {prefix.rstrip('.')}")
    return out


def _id_list(v):
    return (
        isinstance(v, list) and v and all(isinstance(i, dict) and "id" in i for i in v)
    )


def _scalar_list(v):
    return isinstance(v, list) and all(
        isinstance(i, (str, int, float, bool)) or i is None for i in v
    )


def order_like(new, ref):
    """Return ``new`` with keys in ``ref`` order; keys only in ``new`` follow their predecessor."""
    if isinstance(new, dict) and isinstance(ref, dict):
        keys = [k for k in ref if k in new]
        for i, k in enumerate(new):
            if k in keys:
                continue
            prev = [p for p in list(new)[:i] if p in keys]
            keys.insert(keys.index(prev[-1]) + 1 if prev else 0, k)
        return {k: order_like(new[k], ref.get(k)) for k in keys}
    if _id_list(new) and _id_list(ref):
        by_id = {i["id"]: i for i in ref}
        # a new item takes its key order from the first existing sibling
        return [order_like(i, by_id.get(i["id"], ref[0])) for i in new]
    if isinstance(new, list) and isinstance(ref, list) and len(new) == len(ref):
        return [order_like(a, b) for a, b in zip(new, ref)]
    return new


# --- format-preserving io ---------------------------------------------------


def detect_format(text):
    lines = text.splitlines()
    indent = next(
        (len(line) - len(line.lstrip(" ")) for line in lines[1:] if line.strip()), 4
    )
    has_non_ascii = any(ord(c) > 127 for c in text)
    return {
        "indent": indent,
        "newline": "\r\n" if "\r\n" in text else "\n",
        "final_newline": text.endswith("\n"),
        "ensure_ascii": not has_non_ascii
        and re.search(r"\\u[0-9a-fA-F]{4}", text) is not None,
    }


def dump_json(data, fmt):
    s = json.dumps(data, indent=fmt["indent"], ensure_ascii=fmt["ensure_ascii"])
    return s + ("\n" if fmt["final_newline"] else "")


def write_text(path, text, newline):
    # The content is complete before the file is opened, so a failure cannot truncate it
    with open(path, "w", encoding="utf-8", newline=newline) as fh:
        fh.write(text)


def read_raw(path):
    # read_text() would translate CRLF to LF and hide the line ending of the file
    return pathlib.Path(path).read_bytes().decode("utf-8")


def ref_text(pkg, rel, ref):
    r = git(pkg, "show", f"{ref}:{rel}")
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def norm_text(s):
    return s.replace("\r\n", "\n").strip()


# --- subcommands ------------------------------------------------------------


def cmd_map(args):
    for stem, suffix, f, pkg, rel in resolve(args):
        where = f"{pkg.name}/{rel}" if pkg else f"NOT FOUND ({rel}) - new page?"
        print(f"{f.name:55} -> {where}")


def cmd_compare(args):
    for stem, suffix, f, pkg, rel in resolve(args):
        if not pkg:
            print(f"{f.name}: NEW PAGE (no package file found)")
            continue
        remote = ref_text(pkg, rel, args.ref)
        if remote is None:
            print(f"{f.name}: MISSING at {args.ref} ({pkg.name}/{rel})")
            continue
        local = read_raw(f)
        if suffix.endswith(".json"):
            a, b = json.loads(local), json.loads(remote)
            diffs = [] if a == b else diff_paths(a, b)
        else:
            diffs = (
                [] if norm_text(local) == norm_text(remote) else ["~ (text differs)"]
            )
        print(f"{f.name}: {'same' if not diffs else 'DIFF'} vs {args.ref} ({pkg.name})")
        for d in diffs:
            print(f"    {d}")


def _options(values):
    out = {}
    for v in values or []:
        target, _, path = v.partition(":")
        if not path:
            raise SystemExit(f"expected <Stem>.<kind>:<path>, got {v!r}")
        out.setdefault(target, []).append(path)
    return out


def cmd_merge(args):
    keep, drop, allow = (
        _options(args.keep),
        _options(args.drop),
        _options(args.allow_removal),
    )
    planned, errors = [], []
    for stem, suffix, f, pkg, rel in resolve(args):
        if not pkg:
            errors.append(f"{f.name}: no package file found; create new pages by hand")
            continue
        target = pkg / rel
        current = read_raw(target) if target.exists() else None
        remote = ref_text(pkg, rel, args.ref)
        if (
            current is not None
            and remote is not None
            and norm_text(current) != norm_text(remote)
            and not args.allow_dirty
        ):
            # the decisions were made against --ref; other content in the working tree would be lost unseen
            errors.append(
                f"{pkg.name}/{rel}: working tree differs from {args.ref}. Use the ref of the checked-out branch, or --allow-dirty"
            )
            continue
        fmt = detect_format(current) if current else dict(PACKAGE_FORMAT)
        source = read_raw(f)
        if not suffix.endswith(".json"):
            if current is not None and norm_text(current) == norm_text(source):
                print(f"unchanged {target}")
                continue
            # write_text() translates "\n" to the target line ending
            text = norm_text(source) + ("\n" if fmt["final_newline"] else "")
            planned.append((target, text, fmt["newline"], f.name, []))
            continue
        key = f"{stem}.{kind(suffix)}"
        ref_data = json.loads(remote) if remote is not None else {}
        data = json.loads(source)
        for p in drop.get(key, []):
            delete_path(data, p)
        for p in keep.get(key, []):
            set_path(data, p, get_path(ref_data, p))
        diffs = diff_paths(data, ref_data)
        removals = [d[2:] for d in diffs if d.startswith("M ")]
        blocked = [
            r
            for r in removals
            if not any(
                r == a or r.startswith((a + ".", a + "[", a + " (item"))
                for a in allow.get(key, [])
            )
        ]
        if blocked:
            errors.append(
                f"{key}: content exists only at {args.ref} and would be removed:\n"
                + "\n".join(f"    {b}" for b in blocked)
                + f"\n  decide per path: --keep {key}:<path> (merge it) or --allow-removal {key}:<path>"
            )
            continue
        if current is not None and json.loads(current) == data:
            print(f"unchanged {target}")
            continue
        data = order_like(data, json.loads(current) if current else ref_data)
        planned.append((target, dump_json(data, fmt), fmt["newline"], key, diffs))
    if errors:
        print("NOTHING WRITTEN:\n" + "\n".join(errors), file=sys.stderr)
        return 1
    for target, text, newline, label, diffs in planned:
        if args.dry_run:
            print(f"would write {target}")
        else:
            write_text(target, text, newline)
            print(f"wrote {target}")
        for d in diffs:
            print(f"    {d}")
    return 0


def cmd_drop(args):
    path = pathlib.Path(args.file)
    text = read_raw(path)
    fmt = detect_format(text)
    data = json.loads(text)
    for p in args.path:
        delete_path(data, p)
    write_text(path, dump_json(data, fmt), fmt["newline"])
    print(f"removed {len(args.path)} path(s) from {path}")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("map", "compare", "merge"):
        p = sub.add_parser(name)
        p.add_argument("--src", required=True, help="folder with the source files")
        p.add_argument(
            "--suffix",
            action="append",
            required=True,
            help="<source suffix>=<package suffix>, e.g. .jsondata.json=slot_jsondata.json (repeat per file kind)",
        )
        p.add_argument(
            "--name-prefix",
            action="append",
            help="<prefix>=<Namespace>: stems with this prefix are pages named by the jsondata name, e.g. Property_=Property",
        )
        p.add_argument(
            "--packages",
            help="folder with the page package submodules (default: <git toplevel>/packages)",
        )
        p.add_argument(
            "--ref",
            default="origin/main",
            help="git ref to compare with (default: origin/main)",
        )
        p.add_argument(
            "pages", nargs="*", help="source stems to process (default: all)"
        )
        if name == "merge":
            p.add_argument(
                "--keep",
                action="append",
                help="<Stem>.<kind>:<path> take this value from --ref",
            )
            p.add_argument(
                "--drop",
                action="append",
                help="<Stem>.<kind>:<path> leave this out of the package file",
            )
            p.add_argument(
                "--allow-removal",
                action="append",
                help="<Stem>.<kind>:<path> accept that this ref content is removed",
            )
            p.add_argument("--dry-run", action="store_true")
            p.add_argument(
                "--allow-dirty",
                action="store_true",
                help="write although the working tree differs from --ref",
            )
    p = sub.add_parser("drop")
    p.add_argument("file")
    p.add_argument("--path", action="append", required=True)
    args = ap.parse_args()
    if args.cmd != "drop" and not args.packages:
        args.packages = str(default_packages())
    return {
        "map": cmd_map,
        "compare": cmd_compare,
        "merge": cmd_merge,
        "drop": cmd_drop,
    }[args.cmd](args) or 0


if __name__ == "__main__":
    sys.exit(main())
