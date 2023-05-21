from pathlib import Path

from reusable import WorldCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Core",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.core",
    # Package ID - usually the same as repo
    id="world.opensemantic.core",
    # Package subdirectory - usually resembling parts of the package name
    subdir="core",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=(
        "Provides core functionalities of OpenSemanticWorld / OpenSemanticLab"
    ),
    # Specify the package version - use semantic versioning
    version="0.13.0",
    # Author(s)
    author=["Simon Stier", "Lukas Gold"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Module:Lustache",
        "Module:Lustache/Context",
        "Module:Lustache/Renderer",
        "Module:Lustache/Scanner",
        "Module:Entity",
        "Module:MwJson",
        "JsonSchema:MultiLangProperty",
        "JsonSchema:UuidUriProperty",
        "JsonSchema:Label",
        "JsonSchema:Description",
        "JsonSchema:Statement",
        "Category:Category",
        "Category:Entity",
        "Category:Item",
        "Category:OSW2ac4493f8635481eaf1db961b63c8325",  # Data
        # "Category:OSWfe72974590fd4e8ba94cd4e8366375e8", # DataSet
        "Category:OSWff333fd349af4f65a69100405a9e60c7",  # File
        "Category:OSW11a53cdfbdc24524bf8ac435cbf65d9d",  # WikiFile
        "Category:OSWe5aa96bffb1c4d95be7fbd46142ad203",  # Process
        "Category:OSWe427aafafbac4262955b9f690a83405d",  # Tool
        "Category:Property",
        "Category:ObjectProperty",
        "Category:QuantityProperty",
        "Category:OSW1b15ddcf042c4599bd9d431cbfdf3430",  # MainQuantityProperty
        "Category:OSW69f251a900944602a08d1cca830249b5",  # SubQuantityProperty
        "Template:Helper/UI/Tiles/Grid",
        "Template:Helper/UI/Tiles/Tile",
        "Template:Helper/UI/VE/Hidden",
        "Template:Helper/UI/VE/Visible",
        "Template:Helper/UI/Query/ReverseListFormat",
        "Template:Decoration/Annotation",
        "Template:Decoration/ColoredText",
        "Template:Editor/DrawIO",
        "Template:Editor/Graph",
        "Template:Editor/Kekule",
        "Template:Editor/Kekule/Default",
        "Template:Editor/Spreadsheet",
        "Template:Editor/SvgEdit",
        "Template:Editor/Wellplate",
        "Template:Viewer/Kekule",
        "Template:Viewer/Github/Code",
        "Module:Viewer/Github",
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
