"""Delete wiki pages by prefix, namespace, or SMW query.

Usage examples:
  python scripts/delete_pages.py --mode prefix -s "Item:OSW123" --dry-run
  python scripts/delete_pages.py --mode namespace -s "JsonSchema" --dry-run
  python scripts/delete_pages.py --mode query -s "[[Category:OSWabc123]]" -c "cleanup"
  python scripts/delete_pages.py --mode namespace -s "Category" -e "Category:OSW" --dry-run
"""

import argparse
import sys
from pathlib import Path

from osw.auth import CredentialManager
from osw.wtsite import WtSite

SCRIPT_DIR = Path(__file__).parent
CRED_FILEPATH_DEFAULT = SCRIPT_DIR / "accounts.pwd.yaml"
DEFAULT_DOMAIN = "wiki-dev.open-semantic-lab.org"


def find_pages(wtsite: WtSite, mode: str, selector: str, debug: bool) -> list:
    """Return a list of page titles matching the selector."""
    if mode == "prefix":
        if debug:
            print(f"  Prefix search: '{selector}'")
        return wtsite.prefix_search(
            WtSite.SearchParam(query=selector, limit=1000, debug=debug)
        )
    elif mode == "namespace":
        prefix = f"{selector}:"
        if debug:
            print(f"  Namespace search (prefix): '{prefix}'")
        return wtsite.prefix_search(
            WtSite.SearchParam(query=prefix, limit=1000, debug=debug)
        )
    elif mode == "query":
        if debug:
            print(f"  SMW query: '{selector}'")
        return wtsite.semantic_search(
            WtSite.SearchParam(query=selector, limit=1000, debug=debug)
        )
    else:
        print(f"Error: unknown mode '{mode}'", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Delete wiki pages by prefix, namespace, or SMW query.",
        epilog=(
            "Examples:\n"
            '  python scripts/delete_pages.py --mode prefix -s "Item:OSW123" --dry-run\n'
            '  python scripts/delete_pages.py --mode namespace -s "JsonSchema" --dry-run\n'
            '  python scripts/delete_pages.py --mode query -s "[[Category:Entity]]" --dry-run\n'
            '  python scripts/delete_pages.py --mode namespace -s "Category" -e "Category:OSW" --dry-run\n'
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["prefix", "namespace", "query"],
        required=True,
        help="How to select pages: prefix, namespace, or SMW query",
    )
    parser.add_argument(
        "-s", "--selector",
        type=str,
        required=True,
        help="Prefix string, namespace name, or SMW query (e.g. '[[Category:Foo]]')",
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
        default="Deleted via delete_pages.py",
        help="Deletion comment for page history",
    )
    parser.add_argument(
        "-e", "--exclude",
        type=str,
        action="append",
        default=[],
        help=(
            "Exclude pages whose title starts with this prefix (repeatable). "
            "E.g. -e 'Category:OSW' keeps all Category:OSW* pages."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List matching pages without deleting",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print verbose debug output",
    )

    args = parser.parse_args()

    # Connect to wiki
    print(f"Connecting to {args.domain} ...")
    wtsite = WtSite(
        WtSite.WtSiteConfig(
            iri=args.domain,
            cred_mngr=CredentialManager(cred_filepath=Path(args.cred_filepath)),
        )
    )

    # Find pages
    print(f"Finding pages (mode: {args.mode}, selector: '{args.selector}') ...")
    titles = find_pages(wtsite, args.mode, args.selector, args.debug)

    if not titles:
        print("No pages found.")
        sys.exit(0)

    # Apply exclusion filters
    if args.exclude:
        before = len(titles)
        titles = [
            t for t in titles
            if not any(t.startswith(ex) for ex in args.exclude)
        ]
        excluded = before - len(titles)
        if excluded and args.debug:
            print(f"  Excluded {excluded} page(s) matching: {args.exclude}")
        if not titles:
            print("All matched pages were excluded. Nothing to delete.")
            sys.exit(0)

    # Print matched pages
    print(f"\nMatched {len(titles)} page(s):")
    for title in sorted(titles):
        print(f"  {title}")

    if args.dry_run:
        print(f"\n[DRY RUN] {len(titles)} page(s) would be deleted. No changes made.")
        sys.exit(0)

    # Confirm
    response = input(f"\nDelete {len(titles)} page(s)? [y/N]: ").strip().lower()
    if response != "y":
        print("Aborted.")
        sys.exit(0)

    # Delete
    print(f"Deleting {len(titles)} page(s) ...")
    wtsite.delete_page(
        WtSite.DeletePageParam(
            page=titles,
            comment=args.comment,
            parallel=True,
            debug=args.debug,
        )
    )
    print("Done.")


if __name__ == "__main__":
    main()
