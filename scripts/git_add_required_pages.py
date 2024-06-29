import json
from pathlib import Path

import git  # pip install gitpython
from osw.utils.regex_pattern import REGEX_PATTERN_LIB
from osw.utils.strings import RegExPatternExtended
from typing_extensions import List


def list_unstaged_files(package_dir: Path) -> List[Path]:
    """List all unstaged files in the package directory"""
    repo = git.Repo(package_dir)
    return [package_dir / item.a_path for item in repo.index.diff(None)]


def list_untracked_files(package_dir: Path) -> List[Path]:
    """List all untracked files in the package directory"""
    repo = git.Repo(package_dir)
    return [package_dir / item for item in repo.untracked_files]


def list_changed_files(package_dir: Path) -> List[Path]:
    """List all changed files in the package directory"""
    repo = git.Repo(package_dir)
    return [package_dir / item.a_path for item in repo.index.diff("HEAD")]


def read_missing_pages_json(fp: Path) -> list:
    """Read the missing pages json file"""
    with open(fp, "r") as f:
        json_content = json.load(f)
    if isinstance(json_content, dict):
        return list(json_content.keys())
    elif isinstance(json_content, list):
        return json_content


def read_required_pages_json(fp: Path) -> list:
    """Read the required pages json file"""
    with open(fp, "r") as f:
        json_content = json.load(f)
    if isinstance(json_content, dict):
        return json_content["list"]


def get_list_of_file_paths(package_dir: Path, crawl: bool = True) -> list:
    """Get the list of files in the package directory. If crawl is True, the function
    will also list the files in subdirectories (recursively)."""
    if crawl:
        return list(package_dir.rglob("*"))
    else:
        return list(package_dir.iterdir())


def get_osw_ids_from_pages(pages: list) -> list:
    """Get the OSW-IDs from the page titles"""
    pattern = REGEX_PATTERN_LIB["UUID from full page title"]
    osw_ids = []
    for page in pages:
        search_res = pattern.search(page)
        if search_res.match is not None:
            oswid = search_res.groups["Prefix"] + search_res.groups["UUID"]
            osw_ids.append(oswid)
    return osw_ids


def get_osw_id_from_file_path(fp: Path) -> str:
    pattern = RegExPatternExtended(
        description="UUID from file name",
        pattern=r"([A-Z]+)([0-9a-fA-F]{32})((?:\.[\w-]+)*)",
        group_keys=["Prefix", "UUID", "Suffix(es)"],
        example_str="OSWe8c6b659eab14cca927835ccd6baef15.png.slot_header.wikitext",
        expected_groups=[
            "OSW",
            "e8c6b659eab14cca927835ccd6baef15",
            ".png.slot_header.wikitext",
        ],
    )
    file_name = fp.name
    search_res = pattern.search(file_name)
    if search_res.match is not None:
        return search_res.groups["Prefix"] + search_res.groups["UUID"]


def add_selected_files_to_staging_area(package_dir: Path, status: str = None) -> None:
    if status is None:
        status = "untracked"
    required_pages = read_required_pages_json(package_dir / "required_pages.json")
    if status == "untracked":
        file_paths = list_untracked_files(package_dir)
    elif status == "unstaged":
        file_paths = list_unstaged_files(package_dir)
    elif status == "changed":
        file_paths = list_changed_files(package_dir)
    elif status == "all":
        file_paths = get_list_of_file_paths(package_dir)
    else:
        raise ValueError(
            "Invalid status. Choose 'untracked', 'unstaged', 'changed' " "or 'all'."
        )

    for fp in file_paths:
        osw_id = get_osw_id_from_file_path(fp)
        # print(f"File path: {fp}; OSW-ID: {osw_id}")
        # Files without OSW-ID are not considered / should be added manually
        if osw_id is None:
            continue
        # Files listed in the missing pages json file are considered / should be added
        for page in required_pages:
            if osw_id in page:
                print(f"Adding {fp} to the staging area.")
                repo = git.Repo(package_dir)
                repo.git.add(fp)
                break


def main(packages: List[str] = None):
    packages_dir = Path(__file__).parents[1] / "packages"
    if packages is None:
        package_sub_dirs = list(packages_dir.iterdir())
    elif len(packages) == 0:
        package_sub_dirs = list(packages_dir.iterdir())
    else:
        package_sub_dirs = [packages_dir / package for package in packages]

    for package_sub_dir in package_sub_dirs:
        add_selected_files_to_staging_area(package_sub_dir)


if __name__ == "__main__":
    # === enter the package directory name ===
    package_dir_name = "world.opensemantic.meta.docs"
    # ===================================
    # main(packages=[package_dir_name])  # Use for specific packages
    main()  # Use for all
