from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Base",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.base",
    # Package ID - usually the same as repo
    id="world.opensemantic.base",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Provides base items like Article, Person, Project"),
    # Specify the package version - use semantic versioning
    version="0.11.0",
    # Author(s)
    author=["Simon Stier", "Lukas Gold", "Alexander Triol"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26",  # Article
        "Category:OSW494f660e6a714a1a9681c517bbb975da",  # Tutorial
        "Category:OSW0e084decca6f48a7b023d6b7b2c1452d",  # Event
        "Category:OSW81e9e22e7d934382a6a56df7d3736957",  # Recipe
        "Category:OSWa5812d3b5119416c8da1606cbe7054eb",  # Term
        "Category:OSWfe72974590fd4e8ba94cd4e8366375e8", # DataSet
        "Category:OSW3d238d05316e45a4ac95a11d7b24e36b",  # Location
        "Category:OSWf0fe562f422d49c6877490b3dfee2f3f",  # Device
        "Category:OSW02590972aeba46d7864ed492c0c11384",  # Host
        "Category:OSW77e749fc598341ac8b6d2fff21574058",  # Software
        "Category:OSW8c56fd1e858f499da801691c5f2b7309",  # WebService
        "Category:OSW473d7a1ed48544d1be83b258b5810948",  # Site
        "Category:OSW3cb8cef2225e403092f098f99bc4c472",  # OrganizationalUnit
        "Category:OSW44deaa5b806d41a2a88594f562b110e9",  # Person
        "Category:OSWd9aa0bca9b0040d8af6f5c091bf9eec7",  # User
        "Category:OSWb2d7e6a2eff94c82b7f1f2699d5b0ee3",  # Project
        "Category:OSWd22af0aa3b00462a9da9b509538e8926",  # FundingCall
        "Item:OSWf474ec34b7df451ea8356134241aef8a", # State:Done
        "Item:OSWa2b4567ad4874ea1b9adfed19a3d06d1", # State:In work
        "Item:OSWaa8d29404288446a9f3ec7afa4e2a512", # State:To do
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
