"""
This script was created to check the dependencies of each PagePackage. THe
functionality is mostly integrated in osw.controller.page_package and
osw.model.page_package.

todo: integrate the check_required_pages() call into each of the PagePackage
 creation scripts
"""


from pathlib import Path

from osw.controller.page_package import read_package_info

SKRIPTS_TO_SKIP = [
    "check_dependencies.py",
    "org.open-semantic-lab.legacy.properties.py",
    "org.open-semantic-lab.legacy.py",
    "reusable.py",
]


if __name__ == "__main__":
    print("Checking dependencies of page packages...")

    package_scripts = [
        file
        for file in Path(__file__).parent.glob("*.py")
        if file.name not in SKRIPTS_TO_SKIP
    ]

    package_names = [file.stem.replace(".", "_") for file in package_scripts]

    package_infos = [
        read_package_info(script_fp=script_fp, package_name=package_name)
        for script_fp, package_name in zip(package_scripts, package_names)
    ]

    for package_info in package_infos:
        package_name = package_info["package_meta_data"].name
        print(f"Evaluating {package_name}")
        package_info["package_meta_data"].check_required_pages(
            params=package_info["package_creation_config"]
        )

    print("Done.")
