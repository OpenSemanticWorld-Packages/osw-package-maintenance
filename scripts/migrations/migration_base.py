"""Shared infrastructure for versioned migration scripts.

Provides CLI argument parsing, wiki connection, SMW instance querying,
and the migrate-all-pages loop. Each migration script only needs to define:
  - DEFAULT_CATEGORIES: list of category IRIs to query
  - DEFAULT_COMMENT: default edit summary
  - migrate_page(page, page_title, *, log=True) -> bool
"""

import argparse
import sys
from pathlib import Path
from typing import Callable, List, Optional

# Make the parent scripts/ directory importable (for reusable.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reusable import CRED_FILEPATH_DEFAULT

from osw.auth import CredentialManager
from osw.wtsite import WtSite, WtPage

DEFAULT_DOMAIN = "wiki-dev.open-semantic-lab.org"

# Type alias for migrate_page functions
MigratePageFn = Callable[[WtPage, str], bool]


def query_instances(wtsite: WtSite, category: str) -> list:
    """Query all instances of a category and its subcategories via SMW."""
    query = f"[[{category}]]"
    return wtsite.semantic_search(query)


def run_migration(
    *,
    description: str,
    default_categories: List[str],
    default_comment: str,
    migrate_page: MigratePageFn,
    argv: Optional[List[str]] = None,
) -> int:
    """Run a migration with standard CLI, connection, and loop logic.

    Parameters
    ----------
    description:
        One-line description shown in --help.
    default_categories:
        Category IRIs whose instances (and subcategory instances) are queried.
    default_comment:
        Default wiki edit summary.
    migrate_page:
        Function(page, page_title) -> bool. Must call page.set_slot_content
        if it returns True.
    argv:
        Optional argument list (for testing). Defaults to sys.argv[1:].
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-d", "--domain", default=DEFAULT_DOMAIN,
        help=f"Target wiki domain (default: {DEFAULT_DOMAIN})",
    )
    parser.add_argument(
        "--cred-file", type=Path, default=CRED_FILEPATH_DEFAULT,
        help=f"Path to credentials file (default: {CRED_FILEPATH_DEFAULT})",
    )
    parser.add_argument(
        "--execute", action="store_true",
        help="Actually apply changes. Without this flag, runs in dry-run mode.",
    )
    parser.add_argument(
        "--categories", nargs="+", default=default_categories,
        help="Categories whose instances to migrate",
    )
    parser.add_argument(
        "--pages", nargs="+", default=None,
        help="Explicit page titles to migrate (skips SMW query)",
    )
    parser.add_argument(
        "-c", "--comment", default=default_comment,
        help="Edit comment for wiki edits",
    )

    args = parser.parse_args(argv)
    dryrun = not args.execute

    if dryrun:
        print("=== DRY RUN (use --execute to apply changes) ===\n")
    else:
        print("=== EXECUTING MIGRATION ===\n")

    print(f"Connecting to {args.domain}...")
    wtsite = WtSite(
        WtSite.WtSiteConfig(
            iri=args.domain,
            cred_mngr=CredentialManager(cred_filepath=args.cred_file),
        )
    )

    if args.pages:
        page_titles = args.pages
    else:
        page_titles = []
        seen = set()
        for cat in args.categories:
            print(f"Querying instances of {cat}...")
            results = query_instances(wtsite, cat)
            new = [r for r in results if r not in seen]
            seen.update(new)
            print(f"  found {len(results)} instances ({len(new)} new)")
            page_titles.extend(new)

    if not page_titles:
        print("No pages to migrate.")
        return 0

    print(f"\nProcessing {len(page_titles)} pages...\n")

    modified = 0
    skipped = 0
    errors = 0

    for title in page_titles:
        print(f"[{title}]")
        try:
            page = wtsite.get_page(WtSite.GetPageParam(titles=[title])).pages[0]
            was_changed = migrate_page(page, title)
            if was_changed:
                if not dryrun:
                    page.edit(comment=args.comment)
                    print(f"  -> saved")
                else:
                    print(f"  -> would save (dry-run)")
                modified += 1
            else:
                print(f"  -> no changes needed")
                skipped += 1
        except Exception as e:
            print(f"  ERROR: {e}")
            errors += 1

    print(f"\nDone. Modified: {modified}, Skipped: {skipped}, Errors: {errors}")
    if dryrun and modified > 0:
        print(f"\nRe-run with --execute to apply {modified} change(s).")

    return 0 if errors == 0 else 1
