from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Demo - Common",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.demo",
    # Package ID - usually the same as repo
    id="world.opensemantic.demo.common",
    # Package subdirectory - usually resembling parts of the package name
    subdir="common",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Provides common demo content"),
    # Specify the package version - use semantic versioning
    version="0.2.0",
    # Author(s)
    author=["Simon Stier"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Zentrales_Wiki/Landing_page_v2",
        "Item:OSWb894a0c0e11c47d8a0dc591f75c7962c",  # TowardsAnOpenSemanticWorld
        "Item:OSW0e49b7ed40774f0a9788158794cb88cf",  # FemsEuromat2023
        "Item:OSW3a941905208445c2ae5d181646a87de2",  # Porridge
        "Item:OSWea3abf8df16940ba87dc7b68ddcf6e34",  # DemoArticle
        "Item:OSW43b7ce95da134566bc69f221442cfd18",  # DemoProject
        "Item:OSW727ae933ec6d48f18e637e8ffe15e436",  # DemoElnEntry
        "Item:OSW8ec5338887b04936869798218254c1e7",  # DemoUser
        "Item:OSWe0dc3ee6559648659238b9dd4372cb8f",  # Benzene
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
