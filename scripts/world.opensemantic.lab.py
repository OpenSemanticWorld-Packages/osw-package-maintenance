from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Lab",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.lab",
    # Package ID - usually the same as repo
    id="world.opensemantic.lab",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("For material science, etc."),
    # Specify the package version - use semantic versioning
    version="0.6.1",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.base",
    ],
    # Author(s)
    author=["Simon Stier", "Lukas Gold"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Category:OSW182916df3eee472e88e7c8d114a7fe27",  # MaterialType
        "Category:OSW31ca9a739cb24079b36824045c0832aa",  # Material
        "Category:OSW2afce49fe800460a95cf480cc0656757",  # ChemicalSubstanceType
        "Category:OSW0583b134c618484c9911a3dff145c7eb",  # ChemicalCompound
        "Category:OSW25ab317fa369435797b7a92c9fd3bde6",  # Sample type
        "Category:OSW5c6f6eaaa96e4f84ad6f2ea02fc18ce4",  # Sampling
        "Category:OSW88894b63a51d46b08b5b4b05a6b1b3c3",  # MaterialSample
        "Category:OSW29f0a4619cc243679e68b682d3bdb890",  # GeoSample
        "Category:OSW61d19dea4b9c4de8bcbde8036fc0e0a6",  # LabProcessType
        "Category:OSW0e7fab2262fb4427ad0fa454bc868a0d",  # LaboratoryProcess
        "Category:OSW6cc7d1cc87dc4fa8935d5b3d2a9b55c5",  # AnalyticalLabProcessType
        "Category:OSWfa914762adaa4665a63b6a77c3ea6eed",  # AnalyticalLaboratoryProcess
        "Category:OSW293552368bcf4a3681682671f8d47d8f",  # Mixing process
        "Category:OSWb8435fabafcb48f985422448e9df5faa",  # Mixing of chemical substances
        "Category:OSWe2d16d21532a40cfa0abe577629d5c37",  # Test procedure
        "Category:OSWe0572f2791844010962886b892970b4d",  # Controlled environment
        "Category:OSW156137fa74914572ad2998f7f6594bca",  # DataDevice
        "Property:HasCount",
        "Property:HasMass",
        "Property:HasVolume",
        "Property:HasMassConcentration",
        "Property:HasMonetaryValue",
        "Property:HasGravimetricMonetaryValue",
        "Property:HasPricePerWeight",
        "Property:HasVolumetricMonetaryValue",
        "Property:HasPricePerVolume",
        "Property:HasPerUnitMonetaryValue",
        "Property:HasPricePerUnit",
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
