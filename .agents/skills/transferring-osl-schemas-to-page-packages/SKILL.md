---
name: transferring-osl-schemas-to-page-packages
description: Use when OSL category, property or item pages developed in an application repository must be compared with, or moved into, the OpenSemanticWorld page packages under osw-package-maintenance/packages, on main or on a development or deployment branch of a package submodule. Also use when a schema feature must be removed from a package schema.
---

# Transferring OSL schemas to page packages

## Overview

The application repository stores page files under its own naming convention. The page
packages store slot files named by page, and each package is its own git submodule. A
transfer is a **merge, not a copy**: the package ref often has content that the source
lacks, and every such difference needs a decision. `osl_transfer.py` in this folder does
the mapping, the comparison and the writing. Run it with Python 3 from the
`osw-package-maintenance` root. After a change to the tool, run
`python -m unittest test_osl_transfer` in this folder.

## Layout

Package files are in `packages/<pkg>/<subdir>/<Namespace>/` (`<subdir>` is for example
`core` or `base`):

| Page | Package file |
|---|---|
| Category or Item | `Category/<OSW-ID>.slot_<slot>` or `Item/<OSW-ID>.slot_<slot>` |
| Property | `Property/<Name>.slot_<slot>` |

- OSW-ID = `OSW` + the `uuid` from the jsondata, without dashes. `<Name>` = the `name` from the jsondata.
- `<slot>` is for example `jsondata.json`, `jsonschema.json`, `footer_template.wikitext` or `header_template.wikitext`.
- Package files: indent 4, CRLF, no final newline, literal non-ASCII. Source files can use another format (for example indent 2, `\u` escapes, final newline). The tool keeps the target format.

The source naming differs per application repository. Discover it before step 2 and pass
it to every `map`, `compare` and `merge` call:

- `--suffix <source suffix>=<package suffix>`, once per file kind. Exactly one entry must map to `slot_jsondata.json`, because the tool derives the page from that file. Example: `--suffix .jsondata.json=slot_jsondata.json --suffix .footertemplate.txt=slot_footer_template.wikitext`.
- `--name-prefix <prefix>=<Namespace>`, if the source marks pages that are named by `name` (usually Property pages) with a filename prefix. Example: `--name-prefix Property_=Property`. Without a matching prefix, the tool looks up a page by its OSW-ID.
- Run `map` first and check that every source file maps to the expected package file.

Other facts:

- A local submodule is often on a development branch, and the branch can change outside the session. Run `git -C <pkg> branch --show-current` before every commit.
- The version is in `packages.json`, in the page package Item (`<subdir>/Item/...`, if the package has one) and in the build script `scripts/<pkg>.py` of the parent repository.
- `packages.json` `baseURL` names the branch that a wiki installs from. The build script's `branch=` generates it.
- Do not run the build scripts during a transfer. Their `create()` deletes the package subfolder and downloads the pages again from the wiki.

## Workflow

Below, `<naming>` stands for the `--suffix` and `--name-prefix` options from "Layout", and
`osl_transfer.py` stands for `.agents/skills/transferring-osl-schemas-to-page-packages/osl_transfer.py`.

1. Confirm with the user: the pages, the target branch per package, whether to push, and whether to push to the wiki and create tags. Ask only for what is not given.
2. `git -C packages/<pkg> fetch origin`, then map and compare:
   `python osl_transfer.py map --src <source dir> <naming> [Stem ...]`
   `python osl_transfer.py compare --src <source dir> <naming> [--ref origin/main] [Stem ...]`
   Output lines: `L path` exists only in the source, `M path` exists only at the ref, `~ path` differs. Show the user all lines. Each `M` line needs a decision. For a `~` line the source value replaces the package value, so the user must confirm that the package side has no newer change there.
   Use `--ref origin/main` for main or a new branch. For an existing branch, use `--ref origin/<branch>`.
3. Prepare the branch. `compare` reads the ref, so it can run on any checkout. `merge` writes the working tree, so run it only after this step.
   - Existing branch or main: `git switch <branch>`. Then check that `git rev-list --left-right --count <branch>...origin/<branch>` prints `0 0`.
   - New branch: `git switch -c <branch> origin/main`, then `git branch --unset-upstream`. Without this, the branch tracks `origin/main`.
   - Untracked files in the submodule stay in the working tree after the switch. Do not stage them.
   - If the decisions leave no difference for a package (for example every `M` path is kept), that package needs no branch and no commit.
4. Merge, with one option per `M` path:
   `python osl_transfer.py merge --src <dir> <naming> --ref origin/main Stem --keep Stem.jsonschema:properties.name.description --allow-removal "Stem.jsonschema:items_list[id=example.org]"`
   The part before `:` is the source stem and the slot kind (`jsondata`, `jsonschema`, ...). `--keep` takes the value from the ref. It also works for one list item, which is then kept next to the source items. `--allow-removal` accepts the loss. `--drop` leaves source content out. Use `--dry-run` first. The tool also refuses to write when a target file in the working tree differs from `--ref`, because the decisions did not cover that content. Then finish step 3, or choose the ref of the checked-out branch. The tool refuses to write while an `M` path has no decision. It writes only changed files and keeps the target format and key order.
5. If content must also be removed from the source: run `python osl_transfer.py drop <file> --path <path>`. Then search the source repository for copies, for example a generated Python model that embeds the schema, and tests that assert the content. Run the tests. To tell new failures from old ones, compare with a run on the unchanged files (`git stash push -- <files>`, run, `git stash pop`).
6. Check the result:
   - `compare` shows only the intended differences, and `git diff --stat` lists only the intended files.
   - List the `Property:` names that the change adds to `@context`. Many existing properties are in no package and exist only on the wiki, so a missing package file is not an error by itself. Report the new names and ask the user whether they exist on the target wiki or must be created. Create them only when the user asks: `AGENTS.md` lists the slots of a Property page.
7. Bump the version: minor for new properties or schemas, patch for fixes. Change `packages.json`, and the page package Item if the package has one. Set the Item to the new `packages.json` version, also when it was behind before. Change the build script in the parent repository, and leave it uncommitted unless the user says otherwise. If `git diff` shows that the build script already has an uncommitted bump, report it and do not bump it again.
8. On a branch other than main, set `baseURL` in `packages.json` to that branch. Tell the user which value the build script's `branch=` has, because a build run writes that value back.
9. Wiki push, only if the user wants it: follow "Wiki Push Workflow" in `AGENTS.md` (`push_package_changes.py`, with `-d <domain>`). That workflow pushes to the wiki before the git commit.
10. Commit in the submodule and stage only the named files. Do not commit the submodule pointer in the parent repository unless the user asks. Push only after the user agrees. If a `/ship` skill is available, it always opens a pull request, so ask whether to use it or `git push origin <branch>` (`-u` for a new branch). Without `/ship`, use `git push`. Verify with `git ls-remote --heads origin`. Then fetch one changed slot through the `baseURL` with `curl`. GitHub raw content can be up to 5 minutes old.

## Common mistakes

| Mistake | Effect | Prevention |
|---|---|---|
| Copying source files over package files | Removes content that exists only at the ref, and creates whole-file diffs (indent, key order, escapes) | `merge` with explicit decisions |
| Comparing raw text | Formatting differences look like changes | `compare` parses JSON |
| Guessing the source naming | Files are skipped or map to the wrong slot | Discover it, then check with `map` |
| `open(path, "w")` before reading the same file | The file becomes empty | Build the new content first, then write |
| `Path.read_text()` for format detection | CRLF is hidden and the file is written with LF | The tool reads raw bytes |
| `switch -c x origin/main` without `--unset-upstream` | A later push can go to main | Step 3 |
| `baseURL` left at `main` | The wiki installs the old pages from main | Step 8 |
| Removal done only in the package | The source still has the content, for example in the JSON, a generated model or the tests | Step 5 |
| Committing without a branch check | The commit lands on a development branch | `git branch --show-current` |
