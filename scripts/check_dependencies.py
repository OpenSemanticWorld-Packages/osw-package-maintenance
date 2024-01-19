"""
This script was created to check the dependencies of each PagePackage. The
functionality is mostly integrated in osw.controller.page_package and
osw.model.page_package.
"""


from pathlib import Path

from osw.controller.page_package import PagePackageController, read_package_script_file

SCRIPTS_TO_SKIP = [
    "build_packages.py",
    "check_dependencies.py",
    "org.open-semantic-lab.legacy.properties.py",
    "org.open-semantic-lab.legacy.py",
    "reusable.py",
]


def get_package_script_infos(scripts_to_skip: list[str] = None) -> list[dict]:
    """Get the package info from each PagePackage creation script"""
    if scripts_to_skip is None:
        scripts_to_skip = []
    package_scripts = [
        file
        for file in Path(__file__).parent.glob("*.py")
        if file.name not in list(scripts_to_skip)
    ]

    package_names = [file.stem.replace(".", "_") for file in package_scripts]

    return [
        read_package_script_file(script_fp=script_fp_, package_name=package_name_)
        for script_fp_, package_name_ in zip(package_scripts, package_names)
    ]


if __name__ == "__main__":
    print("Checking dependencies of page packages...")

    package_script_infos = get_package_script_infos(scripts_to_skip=SCRIPTS_TO_SKIP)

    for package_script_info in package_script_infos:
        package_name = package_script_info["package_meta_data"].name
        print(f"Evaluating {package_name}")
        package_script_info["package_meta_data"].check_required_pages(
            params=PagePackageController.CheckRequiredPagesParams(
                creation_config=package_script_info["package_creation_config"],
                # Enable the following line to use the package creation script for the
                #  check instead of the package.json (which is only up-to-date after
                #  the execution of the package creation script)
                read_listed_pages_from_script=False,
                script_dir=package_script_info["package_creation_script_fp"].parent,
            )
        )

    print("Done.")

# todo: Check
# - if Templates are also found
# - if modules are also found
