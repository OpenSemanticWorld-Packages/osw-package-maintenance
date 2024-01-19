from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Ontology",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.ontology",
    # Package ID - usually the same as repo
    id="world.opensemantic.ontology",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Provides schemas for ontology terms"),
    # Specify the package version - use semantic versioning
    version="0.5.0",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.core",
    ],
    # Author(s)
    author=["Simon Stier"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Category:OSW379d5a1589c74c82bc0de47938264d00",  # OwlThing
        "Category:OSW725a3cf5458f4daea86615fcbd0029f8",  # OwlClass
        "Category:OSW6b9ef2784a934b8ab96523366e23e906",  # OwlIndividual
        "Category:OSW57beed5e1294434ba77bb6516e461456",  # EmmoClass
        "Category:OSW9deb690d6ebb4eaaa1ca5a24c2f32cad",  # OeoTerm
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
