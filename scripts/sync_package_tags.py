"""Sync git tags with package versions from packages.json.

For each package submodule, walks the git history to find commits where
the version in packages.json changed, and creates the corresponding
git tag (v<version>) on that commit if it doesn't already exist.

Also warns about inconsistencies:
- Version in packages.json with no corresponding git tag
- Git tags with no corresponding version in packages.json history
- Multiple commits claiming the same version
- Current HEAD version not matching latest tag

Usage:
    # Dry-run (default): show what tags would be created
    python scripts/sync_package_tags.py

    # Create missing tags locally
    python scripts/sync_package_tags.py --apply

    # Also push tags to remote
    python scripts/sync_package_tags.py --apply --push

    # Process specific packages only
    python scripts/sync_package_tags.py --packages world.opensemantic.core world.opensemantic.base
"""

import argparse
import json
import sys
from pathlib import Path

import git


PACKAGES_DIR = Path(__file__).parents[1] / "packages"


def get_version_from_packages_json(content: str) -> str | None:
    """Extract version from packages.json content string."""
    try:
        data = json.loads(content)
        packages = data.get("packages", {})
        if not packages:
            return None
        # Take the first (usually only) package entry
        first_package = next(iter(packages.values()))
        return first_package.get("version")
    except (json.JSONDecodeError, StopIteration, AttributeError):
        return None


def get_version_history(repo: git.Repo) -> list[tuple[str, str, str]]:
    """Walk git history and find all commits where packages.json version changed.

    Returns list of (version, commit_sha, commit_summary) oldest-first.
    """
    history = []
    prev_version = None

    # Walk commits oldest-first
    commits = list(repo.iter_commits("HEAD", paths="packages.json"))
    commits.reverse()  # oldest first

    for commit in commits:
        try:
            blob = commit.tree / "packages.json"
            content = blob.data_stream.read().decode("utf-8")
            version = get_version_from_packages_json(content)
        except (KeyError, UnicodeDecodeError):
            continue

        if version and version != prev_version:
            history.append((version, commit.hexsha, commit.summary))
            prev_version = version

    return history


def get_existing_tags(repo: git.Repo) -> dict[str, str]:
    """Get existing version tags as {version: commit_sha}."""
    tags = {}
    for tag in repo.tags:
        name = tag.name
        if name.startswith("v"):
            version = name[1:]
            tags[version] = tag.commit.hexsha
    return tags


def process_package(
    package_path: Path,
    *,
    apply: bool = False,
    push: bool = False,
) -> tuple[int, int, int]:
    """Process a single package. Returns (tags_created, warnings, errors)."""
    name = package_path.name
    tags_created = 0
    warnings = 0
    errors = 0

    try:
        repo = git.Repo(package_path)
    except git.InvalidGitRepositoryError:
        print(f"  SKIP: not a git repository")
        return 0, 0, 0

    if repo.bare:
        print(f"  SKIP: bare repository")
        return 0, 0, 0

    # Get current version from packages.json on disk
    packages_json_path = package_path / "packages.json"
    if not packages_json_path.exists():
        print(f"  SKIP: no packages.json")
        return 0, 0, 0

    current_version = get_version_from_packages_json(
        packages_json_path.read_text(encoding="utf-8")
    )
    if not current_version:
        print(f"  WARN: could not parse version from packages.json")
        return 0, 1, 0

    # Get version history and existing tags
    version_history = get_version_history(repo)
    existing_tags = get_existing_tags(repo)

    if not version_history:
        print(f"  WARN: no version changes found in git history")
        return 0, 1, 0

    # Check for versions that appear multiple times (shouldn't happen)
    version_commits = {}
    for version, sha, summary in version_history:
        version_commits.setdefault(version, []).append((sha, summary))

    for version, commits in version_commits.items():
        if len(commits) > 1:
            print(f"  WARN: version {version} appears in {len(commits)} commits:")
            for sha, summary in commits:
                print(f"    {sha[:8]} {summary}")
            warnings += 1

    # Check for orphaned tags (tags without a matching version in history)
    history_versions = {v for v, _, _ in version_history}
    for tag_version in sorted(existing_tags):
        if tag_version not in history_versions:
            print(f"  WARN: tag v{tag_version} has no matching version change in history")
            warnings += 1

    # Create missing tags
    for version, sha, summary in version_history:
        tag_name = f"v{version}"

        if version in existing_tags:
            # Tag exists — check if it points to the right commit
            if existing_tags[version] != sha:
                print(
                    f"  WARN: tag {tag_name} points to {existing_tags[version][:8]} "
                    f"but version was set in {sha[:8]} ({summary})"
                )
                warnings += 1
            continue

        # Tag is missing
        if apply:
            try:
                repo.create_tag(tag_name, ref=sha, message=f"Release {version}")
                print(f"  CREATED: {tag_name} -> {sha[:8]} ({summary})")
                tags_created += 1

                if push:
                    origin = repo.remote("origin")
                    origin.push(tag_name)
                    print(f"    PUSHED: {tag_name}")
            except git.GitCommandError as e:
                print(f"  ERROR: failed to create tag {tag_name}: {e}")
                errors += 1
        else:
            print(f"  MISSING: {tag_name} -> {sha[:8]} ({summary})")
            tags_created += 1  # count as "would create"

    # Check HEAD version consistency
    head_sha = repo.head.commit.hexsha
    latest_history_version = version_history[-1][0] if version_history else None
    latest_history_sha = version_history[-1][1] if version_history else None

    if current_version != latest_history_version:
        print(
            f"  WARN: working dir version ({current_version}) differs from "
            f"latest committed version ({latest_history_version}) — uncommitted change?"
        )
        warnings += 1

    return tags_created, warnings, errors


def main():
    parser = argparse.ArgumentParser(
        description="Sync git tags with package versions from packages.json.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually create missing tags (default: dry-run)",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push created tags to origin (requires --apply)",
    )
    parser.add_argument(
        "--packages",
        nargs="+",
        metavar="NAME",
        help="Process only these packages (e.g. world.opensemantic.core)",
    )
    args = parser.parse_args()

    if args.push and not args.apply:
        print("Error: --push requires --apply", file=sys.stderr)
        sys.exit(1)

    if not args.apply:
        print("=== DRY RUN (use --apply to create tags) ===\n")

    # Discover packages
    if args.packages:
        package_dirs = [PACKAGES_DIR / name for name in args.packages]
    else:
        package_dirs = sorted(
            p for p in PACKAGES_DIR.iterdir()
            if p.is_dir() and (p / "packages.json").exists()
        )

    total_created = 0
    total_warnings = 0
    total_errors = 0

    for package_path in package_dirs:
        if not package_path.exists():
            print(f"{package_path.name}: NOT FOUND")
            total_errors += 1
            continue

        print(f"{package_path.name}:")
        created, warns, errs = process_package(
            package_path, apply=args.apply, push=args.push
        )
        total_created += created
        total_warnings += warns
        total_errors += errs
        if created == 0 and warns == 0 and errs == 0:
            print("  OK")
        print()

    # Summary
    action = "Created" if args.apply else "Would create"
    print(f"--- Summary ---")
    print(f"{action}: {total_created} tag(s)")
    print(f"Warnings: {total_warnings}")
    print(f"Errors: {total_errors}")

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
