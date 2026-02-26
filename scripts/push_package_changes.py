"""Push local OSW package changes to a wiki instance.

Detects changed files in a package via git (unstaged diffs, staged diffs,
or last N commits), maps them to OSW pages using packages.json, and pushes
the updated slot content to the target wiki with the commit message as
edit comment.

Usage examples:
    # Dry-run: preview what last commit would push
    python scripts/push_package_changes.py packages/world.opensemantic.core --mode commits --dry-run

    # Push staged changes with a custom edit comment
    python scripts/push_package_changes.py packages/world.opensemantic.base --mode staged -c "Update schema"

    # Push last 3 commits to a specific wiki
    python scripts/push_package_changes.py packages/world.opensemantic.core --mode commits -n 3 -d osl-sandbox.big-map.eu
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union

import git

from reusable import CRED_FILEPATH_DEFAULT
from osw.auth import CredentialManager
from osw.model.page_package import NAMESPACE_CONST_TO_NAMESPACE_MAPPING
from osw.wtsite import WtSite, WtPage

DEFAULT_DOMAIN = "wiki-dev.open-semantic-lab.org"

NAMESPACE_DIRS = {
    "Category", "Item", "Module", "JsonSchema", "Template", "Property", "File",
}


def load_packages_json(package_path: Path) -> dict:
    """Read and parse packages.json from a package directory."""
    packages_json_path = package_path / "packages.json"
    if not packages_json_path.exists():
        raise FileNotFoundError(f"No packages.json found at {packages_json_path}")
    with open(packages_json_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_urlpath_to_page_index(packages_json: dict) -> Dict[str, dict]:
    """Build a reverse index: urlPath -> {page_entry, slot_name, page_title}.

    This maps every file path referenced in packages.json back to the page
    and slot it belongs to.
    """
    index = {}
    for _package_name, package_data in packages_json.get("packages", {}).items():
        for page_entry in package_data.get("pages", []):
            namespace = NAMESPACE_CONST_TO_NAMESPACE_MAPPING.get(
                page_entry["namespace"], page_entry["namespace"]
            )
            page_title = f"{namespace}:{page_entry['name']}"

            # Index the main slot
            main_url_path = page_entry.get("urlPath")
            if main_url_path:
                index[main_url_path] = {
                    "page_entry": page_entry,
                    "slot_name": "main",
                    "page_title": page_title,
                }

            # Index additional slots
            for slot_name, slot_data in page_entry.get("slots", {}).items():
                slot_url_path = slot_data.get("urlPath")
                if slot_url_path:
                    index[slot_url_path] = {
                        "page_entry": page_entry,
                        "slot_name": slot_name,
                        "page_title": page_title,
                    }
    return index


def find_subdir(package_path: Path) -> str:
    """Detect the content subdirectory of a package.

    Each package has a single subdir containing namespace folders (Category/,
    Item/, etc.). For example, world.opensemantic.core uses 'core/'.
    Returns empty string if namespace dirs are directly in package_path.
    """
    for child in sorted(package_path.iterdir()):
        if child.is_dir() and child.name not in {".git", "__pycache__", ".github"}:
            sub_contents = {c.name for c in child.iterdir() if c.is_dir()}
            if sub_contents & NAMESPACE_DIRS:
                return child.name
    # Check if namespace dirs are directly in the package root
    direct_contents = {c.name for c in package_path.iterdir() if c.is_dir()}
    if direct_contents & NAMESPACE_DIRS:
        return ""
    raise ValueError(f"Could not determine content subdir for package at {package_path}")


def _collect_diff_paths(diffs) -> Tuple[Set[str], Set[str]]:
    """Extract file paths from git diff items, separating deletions.

    Returns:
        (changed, deleted) — two sets of file paths.
    """
    changed: Set[str] = set()
    deleted: Set[str] = set()
    for diff_item in diffs:
        if diff_item.change_type == "D":
            # File was deleted — use a_path (the path before deletion)
            if diff_item.a_path:
                deleted.add(diff_item.a_path)
        else:
            # Added, modified, renamed, etc.
            if diff_item.a_path:
                changed.add(diff_item.a_path)
            if diff_item.b_path and diff_item.b_path != diff_item.a_path:
                changed.add(diff_item.b_path)
    return changed, deleted


class _Batch:
    """One unit of work: files changed/deleted in a single commit or diff."""
    __slots__ = ("changed", "deleted", "comment", "tree")

    def __init__(
        self,
        changed: List[str],
        deleted: List[str],
        comment: str,
        tree: Optional[git.objects.tree.Tree],
    ):
        self.changed = changed
        self.deleted = deleted
        self.comment = comment
        self.tree = tree


def detect_changed_files(
    package_path: Path,
    mode: str,
    num_commits: int = 1,
) -> List[_Batch]:
    """Detect changed files in a package's git repo.

    Returns a list of _Batch objects. For unstaged/staged mode this is a single
    batch with tree=None (read from disk). For commits mode each commit produces
    its own batch, ordered oldest-first so wiki edits replay chronologically.
    """
    repo = git.Repo(package_path)

    if mode == "unstaged":
        changed, deleted = _collect_diff_paths(repo.index.diff(None))
        return [_Batch(sorted(changed), sorted(deleted), "", None)]

    if mode == "staged":
        changed, deleted = _collect_diff_paths(repo.index.diff("HEAD"))
        return [_Batch(sorted(changed), sorted(deleted), "", None)]

    # mode == "commits"
    commits = list(repo.iter_commits("HEAD", max_count=num_commits))
    batches = []
    for commit in commits:
        if commit.parents:
            # Forward diff: parent → commit
            diffs = commit.parents[0].diff(commit)
            changed, deleted = _collect_diff_paths(diffs)
        else:
            # Initial commit — all files are additions
            changed = {
                item.path for item in commit.tree.traverse()
                if item.type == "blob"
            }
            deleted = set()
        batches.append(_Batch(
            sorted(changed), sorted(deleted), commit.message.strip(), commit.tree
        ))
    # Reverse so oldest commit is pushed first (matches chronological order)
    batches.reverse()
    return batches


def _strip_subdir(file_path: str, subdir: str) -> str:
    """Strip the package subdir prefix and normalise separators."""
    if subdir and file_path.startswith(subdir + "/"):
        file_path = file_path[len(subdir) + 1:]
    return file_path.replace("\\", "/")


def map_files_to_pages(
    changed_files: List[str],
    deleted_files: List[str],
    urlpath_index: Dict[str, dict],
    subdir: str,
) -> Dict[str, dict]:
    """Map changed/deleted file paths to page titles and their affected slots.

    Returns:
        Dict mapping page_title -> {page_entry, changed_slots: set,
        deleted_slots: set}.
    """
    pages_to_update: Dict[str, dict] = {}
    unmapped_files = []

    def _ensure_page(info):
        pt = info["page_title"]
        if pt not in pages_to_update:
            pages_to_update[pt] = {
                "page_entry": info["page_entry"],
                "changed_slots": set(),
                "deleted_slots": set(),
            }
        return pt

    for file_path in changed_files:
        relative_path = _strip_subdir(file_path, subdir)
        if relative_path in urlpath_index:
            info = urlpath_index[relative_path]
            pt = _ensure_page(info)
            pages_to_update[pt]["changed_slots"].add(info["slot_name"])
        else:
            unmapped_files.append(file_path)

    for file_path in deleted_files:
        relative_path = _strip_subdir(file_path, subdir)
        if relative_path in urlpath_index:
            info = urlpath_index[relative_path]
            pt = _ensure_page(info)
            pages_to_update[pt]["deleted_slots"].add(info["slot_name"])
        else:
            unmapped_files.append(file_path)

    if unmapped_files:
        print(
            f"Note: {len(unmapped_files)} changed file(s) not mapped to any page "
            f"(e.g. packages.json, README):"
        )
        for f in unmapped_files:
            print(f"  - {f}")

    return pages_to_update


def read_slot_content(
    package_path: Path,
    subdir: str,
    url_path: str,
    tree: Optional[git.objects.tree.Tree] = None,
) -> Optional[Union[str, dict]]:
    """Read a single slot file's content.

    If *tree* is given, reads from that git tree (for replaying commits).
    Otherwise reads from the working directory on disk.
    Returns parsed JSON for .json files, raw text otherwise, or None if missing.
    """
    if tree is not None:
        return _read_slot_from_tree(tree, subdir, url_path)

    if subdir:
        file_path = package_path / subdir / url_path
    else:
        file_path = package_path / url_path

    if not file_path.exists():
        return None

    content = file_path.read_text(encoding="utf-8")
    if not content:
        return None

    if url_path.endswith(".json"):
        return json.loads(content)
    return content


def _read_slot_from_tree(
    tree: git.objects.tree.Tree, subdir: str, url_path: str
) -> Optional[Union[str, dict]]:
    """Read a slot file from a git commit tree."""
    blob_path = f"{subdir}/{url_path}" if subdir else url_path
    try:
        blob = tree / blob_path
    except KeyError:
        return None

    content = blob.data_stream.read().decode("utf-8")
    if not content:
        return None

    if url_path.endswith(".json"):
        return json.loads(content)
    return content


def print_batch_summary(
    batch_index: int,
    total_batches: int,
    pages_to_update: Dict[str, dict],
    edit_comment: str,
    dry_run: bool,
) -> None:
    """Print a human-readable summary for one push batch."""
    prefix = "[DRY RUN] " if dry_run else ""
    if total_batches > 1:
        print(f"\n{prefix}Batch {batch_index}/{total_batches} "
              f"({len(pages_to_update)} page(s))")
    else:
        print(f"\n{prefix}Pages to update: {len(pages_to_update)}")
    print(f"  Edit comment: {edit_comment}")
    for page_title in sorted(pages_to_update):
        info = pages_to_update[page_title]
        parts = []
        if info["changed_slots"]:
            parts.append(", ".join(sorted(info["changed_slots"])))
        if info["deleted_slots"]:
            parts.append("DEL: " + ", ".join(sorted(info["deleted_slots"])))
        print(f"    {page_title}  [{'; '.join(parts)}]")


def push_pages(
    pages_to_update: Dict[str, dict],
    package_path: Path,
    subdir: str,
    domain: str,
    cred_filepath: Path,
    edit_comment: str,
    dry_run: bool,
    debug: bool,
    push_all_slots: bool = False,
    tree: Optional[git.objects.tree.Tree] = None,
) -> None:
    """Push changed pages to the wiki instance.

    If *tree* is provided, file content is read from that git tree rather than
    the working directory. This is used in commits mode to replay each commit's
    actual content.
    """
    if dry_run:
        print("[DRY RUN] No changes pushed.")
        return

    wtsite = WtSite(
        WtSite.WtSiteConfig(
            iri=domain,
            cred_mngr=CredentialManager(cred_filepath=cred_filepath),
        )
    )

    total = len(pages_to_update)
    for idx, page_title in enumerate(sorted(pages_to_update), 1):
        info = pages_to_update[page_title]
        page_entry = info["page_entry"]
        changed_slots = info["changed_slots"]
        deleted_slots = info["deleted_slots"]

        print(f"[{idx}/{total}] {page_title} ...", end=" ", flush=True)

        page = WtPage(wtSite=wtsite, title=page_title, do_init=False)

        # --- changed (or all) slots: read content and set ---
        if push_all_slots:
            slots_to_push = {}
            main_url = page_entry.get("urlPath")
            if main_url:
                slots_to_push["main"] = main_url
            for slot_name, slot_data in page_entry.get("slots", {}).items():
                url = slot_data.get("urlPath")
                if url:
                    slots_to_push[slot_name] = url
        else:
            slots_to_push = {}
            if "main" in changed_slots:
                main_url = page_entry.get("urlPath")
                if main_url:
                    slots_to_push["main"] = main_url
            for slot_name in changed_slots:
                if slot_name != "main":
                    slot_data = page_entry.get("slots", {}).get(slot_name, {})
                    url = slot_data.get("urlPath")
                    if url:
                        slots_to_push[slot_name] = url

        edits = 0
        for slot_name, url_path in slots_to_push.items():
            content = read_slot_content(package_path, subdir, url_path, tree=tree)
            if content is not None:
                page.set_slot_content(slot_name, content)
                edits += 1
                if debug:
                    preview = str(content)[:80]
                    print(f"\n    slot '{slot_name}': {preview}...")
            else:
                # File missing or empty — git says it changed, so push empty
                # to clear the slot (same as a deletion)
                page.set_slot_content(slot_name, "")
                edits += 1
                if debug:
                    print(f"\n    slot '{slot_name}': empty (cleared)")

        # --- deleted slots: set to empty string to remove in MediaWiki ---
        for slot_name in deleted_slots:
            page.set_slot_content(slot_name, "")
            edits += 1
            if debug:
                print(f"\n    slot '{slot_name}': DELETED (set to empty)")

        if edits > 0:
            page.edit(comment=edit_comment)
            print("done")
        else:
            print("skipped (nothing to push)")

    print(f"\n{total} page(s) processed.")


def main():
    parser = argparse.ArgumentParser(
        description="Push local OSW package changes to a wiki instance.",
        epilog=(
            "Examples:\n"
            "  python scripts/push_package_changes.py packages/world.opensemantic.core "
            "--mode commits --dry-run\n"
            "  python scripts/push_package_changes.py packages/world.opensemantic.base "
            "--mode staged -c 'Update schema'\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "package_path",
        type=str,
        help="Path to the package directory (e.g. packages/world.opensemantic.core)",
    )
    parser.add_argument(
        "--mode",
        choices=["unstaged", "staged", "commits"],
        required=True,
        help="How to detect changed files",
    )
    parser.add_argument(
        "-n", "--num-commits",
        type=int,
        default=1,
        help="Number of commits to consider (only for --mode commits, default: 1)",
    )
    parser.add_argument(
        "-d", "--domain",
        type=str,
        default=DEFAULT_DOMAIN,
        help=f"Target wiki domain (default: {DEFAULT_DOMAIN})",
    )
    parser.add_argument(
        "--cred-filepath",
        type=str,
        default=str(CRED_FILEPATH_DEFAULT),
        help="Path to credentials YAML file",
    )
    parser.add_argument(
        "-c", "--comment",
        type=str,
        default=None,
        help=(
            "Edit comment (required for unstaged/staged mode; "
            "overrides commit messages for commits mode)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without pushing to wiki",
    )
    parser.add_argument(
        "--full-page",
        action="store_true",
        help="Push all slots for affected pages, not just changed slots",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print verbose debug output",
    )

    args = parser.parse_args()

    # Resolve package path
    repo_root = Path(__file__).parents[1]
    package_path = Path(args.package_path)
    if not package_path.is_absolute():
        package_path = repo_root / package_path
    package_path = package_path.resolve()

    if not package_path.exists():
        print(f"Error: Package path does not exist: {package_path}", file=sys.stderr)
        sys.exit(1)

    # Validate comment requirement
    if args.mode in ("unstaged", "staged") and args.comment is None:
        print(
            f"Error: --comment / -c is required for --mode {args.mode}",
            file=sys.stderr,
        )
        sys.exit(1)

    # 1. Load packages.json
    print(f"Package: {package_path.name}")
    packages_json = load_packages_json(package_path)

    # 2. Build URL path index
    urlpath_index = build_urlpath_to_page_index(packages_json)
    if args.debug:
        print(f"  Indexed {len(urlpath_index)} file paths across all pages")

    # 3. Detect subdir
    subdir = find_subdir(package_path)
    if args.debug:
        print(f"  Content subdir: '{subdir}'")

    # 4. Detect changed files (returns list of batches)
    print(f"Detecting changes (mode: {args.mode}) ...")
    batches = detect_changed_files(package_path, args.mode, args.num_commits)

    # Build per-batch page mappings and determine edit comments
    push_batches = []  # list of (pages_to_update, edit_comment, tree_or_None)
    for batch in batches:
        if not batch.changed and not batch.deleted:
            continue

        if args.debug:
            if batch.changed:
                print(f"  Changed files ({len(batch.changed)}):")
                for f in batch.changed:
                    print(f"    {f}")
            if batch.deleted:
                print(f"  Deleted files ({len(batch.deleted)}):")
                for f in batch.deleted:
                    print(f"    {f}")

        pages_to_update = map_files_to_pages(
            batch.changed, batch.deleted, urlpath_index, subdir
        )
        if not pages_to_update:
            continue

        edit_comment = args.comment if args.comment else batch.comment
        if not edit_comment:
            edit_comment = "[bot] update of page content"

        push_batches.append((pages_to_update, edit_comment, batch.tree))

    if not push_batches:
        print("No changed files matched any pages in packages.json. Nothing to push.")
        sys.exit(0)

    # 5. Print summary for all batches
    for idx, (pages_to_update, edit_comment, _tree) in enumerate(push_batches, 1):
        print_batch_summary(
            idx, len(push_batches), pages_to_update, edit_comment, args.dry_run
        )
    print()

    # 6. Confirmation (unless dry-run)
    if not args.dry_run:
        response = input("Proceed with push? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            sys.exit(0)

    # 7. Push each batch sequentially
    for idx, (pages_to_update, edit_comment, tree) in enumerate(push_batches, 1):
        if len(push_batches) > 1:
            print(f"\n--- Batch {idx}/{len(push_batches)}: {edit_comment} ---")
        push_pages(
            pages_to_update=pages_to_update,
            package_path=package_path,
            subdir=subdir,
            domain=args.domain,
            cred_filepath=Path(args.cred_filepath),
            edit_comment=edit_comment,
            dry_run=args.dry_run,
            debug=args.debug,
            push_all_slots=args.full_page,
            tree=tree,
        )


if __name__ == "__main__":
    main()
