from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Basic Characteristics",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.characteristics.basic",
    # Package ID - usually the same as repo
    id="world.opensemantic.characteristics.basic",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Contains fundamental qualities"),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.core",
    ],
    # Author(s)
    author=["Simon Stier"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Category:OSW93ccae36243542ceac6c951450a81d47", # "Characteristic"
        "Category:OSWffe74f291d354037b318c422591c5023", # "Characteristic Type"
        "Category:OSW6ef70c808fb54abbbacb059c285713d4", # "Ontology related"
    ],
)
# Provide the information needed (only) to create the page package
package_creation_config = WorldCreat(
    # Specify the path to the working directory - where the package is stored on disk
    working_dir=Path(__file__).parents[1]
    / "packages"
    / package_meta_data.repo,
)

if __name__ == "__main__":
    # Create the page package
    package_meta_data.create(
        creation_config=package_creation_config,
    )
    # Check if all required pages are present
    package_meta_data.check_required_pages(
        params=WorldMeta.CheckRequiredPagesParams(
            creation_config=package_creation_config,
            # Enable the following line to use the package creation script for the
            #  check of listed pages in the requiredPackages instead of the
            #  package.json (which is only up-to-date after the execution of the
            #  package creation script)
            read_listed_pages_from_script=True,
            script_dir=Path(__file__).parent,
        )
    )
