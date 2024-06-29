import json
from datetime import datetime as dt
from pathlib import Path


def per_package(fp: Path) -> dict:
    """Read the package json file"""
    package_dir = fp.parent
    sub_dirs = [item for item in package_dir.iterdir() if item.is_dir()]

    pages_with_non_existing_wikitext = []
    non_existing_slots = []

    with open(fp, "r") as f:
        json_content = json.load(f)
    package_files_exist = {}
    for package in json_content["packages"].keys():
        pages = json_content["packages"][package]["pages"]
        page_files_exist = {}
        for page in pages:
            name = page["name"]
            url_paths = [page["urlPath"]]
            if "slots" in page.keys():
                slots = page["slots"]
                for slot in slots.keys():
                    if slots[slot] is not None:
                        if "urlPath" in slots[slot].keys():
                            url_paths.append(slots[slot]["urlPath"])
            files_exist = {}
            wikitext_exist = False
            for ii, up in enumerate(url_paths):
                file_exists = False
                for sub_dir in sub_dirs:
                    path_to_test = sub_dir / up
                    if path_to_test.exists():
                        file_exists = True
                        break
                if ii == 0:
                    wikitext_exist = file_exists
                    if not wikitext_exist:
                        pages_with_non_existing_wikitext.append(name)
                if not file_exists:
                    non_existing_slots.append({"Page name": name, "urlPath": up})
                files_exist[up] = file_exists
            page_files_exist[name] = {
                "wikitext": wikitext_exist,
                "all slots": files_exist,
            }
        package_files_exist[package] = page_files_exist
    return {
        "Pages with non-existing wikitext": pages_with_non_existing_wikitext,
        "Non-existing slots": non_existing_slots,
        "Package files existence": package_files_exist,
    }


def main():
    package_dir = Path(__file__).parents[1] / "packages"
    # Crawl through package_dir and find all packages.json
    packages = [path for path in package_dir.glob("*") if path.is_dir()]
    packages_files = []
    for package in packages:
        packages_files.extend(list(package.glob("packages.json")))

    for packages_file in packages_files:
        timestamp = {"Last updated": dt.now().strftime("%Y-%m-%d %H:%M:%S")}
        package_info = per_package(fp=packages_file)
        to_export = {**timestamp, **package_info}
        with open(
            packages_file.parent / "files_listed_in_packages_status.json", "w"
        ) as f:
            json.dump(to_export, f, indent=4)


if __name__ == "__main__":
    main()
