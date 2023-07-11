from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Virtual Lab Demo",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.demo.lab.virtual",
    # Package ID - usually the same as repo
    id="world.opensemantic.demo.lab.virtual",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Demo content for modelling, simulation and optimization"),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Author(s)
    author=["Simon Stier"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Category:OSW553f78cc66194ae1873241207b906c4b",  # BattmoModel
        "Item:OSWe7c08b2300f04d0bbb0a55bca8838437", # BattmoSimulation
        "Item:OSWb80747f1ccf340d790955572d27f678c", # BattmoAtinaryOptimization,
        "Category:OSW72eae3c8f41f4a22a94dbc01974ed404", # PrefectFlow
        "Item:OSW491b595f6a024205845bcdf82e6eff79", # BattmoSimulationFlow,
        "Item:OSWff7a28d9e90c4a2d8566d9e95313abb3", # BattmoAtinaryOptimizationFlow,
        "Item:OSWb3f78502f5bf4aea91819131e30e5d69", # BattmoVM
        "Property:HasEnergyDensity"
    ],
)
# Provide the information needed (only) to create the page package
package_creation_config = WorldCreat(
    # Specify the path to the working directory - where the package is stored on disk
    working_dir=Path(__file__).parents[1]
    / "packages"
    / package_meta_data.repo,
)
# Create the page package
package_meta_data.create(
    creation_config=package_creation_config,
)
