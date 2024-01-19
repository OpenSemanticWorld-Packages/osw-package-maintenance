"""
This script was created to build all PagePackage. The
functionality is mostly integrated in osw.controller.page_package and
osw.model.page_package.
"""


from check_dependencies import SCRIPTS_TO_SKIP, get_package_script_infos

if __name__ == "__main__":
    print("Building page packages...")

    package_infos = get_package_script_infos(scripts_to_skip=SCRIPTS_TO_SKIP)
    for package_info in package_infos:
        package_name = package_info["package_meta_data"].name
        print(f"Evaluating {package_name}")
        package_info["package_meta_data"].create(
            creation_config=package_info["package_creation_config"]
        )

    print("Done.")
