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
    version="0.49.6",
    # Specify the required MediaWiki extensions
    requiredExtensions=["OpenSemanticLab", "ExternalData", "WikiMarkdown"],
    # Specify the required PagePackages
    requiredPackages=[],
    # Author(s)
    author=["Simon Stier", "Lukas Gold", "Andreas Räder"],
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
        "JsonSchema:QuantityProperty",
        "JsonSchema:Meta",
        "JsonSchema:SerialNumber",
        "JsonSchema:TypeNumber",
        "JsonSchema:Manufacturer",
        "JsonSchema:DataSheet",
        "JsonSchema:SafetyDataSheet",
        "JsonSchema:Manual",
        "JsonSchema:Instructions",
        "JsonSchema:WikiFile",
        "Category:Category",
        "Category:Entity",
        "Category:Item",
        "Category:Term",
        "Category:OSW379d5a1589c74c82bc0de47938264d00",  # OwlThing
        "Category:OSW5f0dff1c477e45e7ad45e4e247e28f35",  # Documentation Extension
        "Category:OSW2ac4493f8635481eaf1db961b63c8325",  # Data
        "Category:OSWff333fd349af4f65a69100405a9e60c7",  # File
        "Category:OSW3e3f5dd4f71842fbb8f270e511af8031",  # LocalFile
        "Category:OSW05b244d0a669436e96fe4e1631d5a171",  # RemoteFile
        "Category:OSW11a53cdfbdc24524bf8ac435cbf65d9d",  # WikiFile
        "Category:OSWc11438cd6c814ed1a5a253555ee351b4",  # ProcessType
        "Category:OSWe5aa96bffb1c4d95be7fbd46142ad203",  # Process
        "Category:OSWc5d4829ed2744a219ba027171c75fa1d",  # Task
        "Category:OSWcbb09a36336740c6a2cd62db9bf647ec",  # IntangibleItem
        "Category:OSWca99a9bb9ad24386b222d18a73c2af5e",  # Physical Item Type
        "Category:OSW37a57741ae2e4dd4b29b1172b6848be8",  # Physical Item
        "Category:OSWa5812d3b5119416c8da1606cbe7054eb",  # DefinedTerm (moved from base)
        "Category:OSW09f6cdd54bc54de786eafced5f675cbe",  # Keyword
        "Item:OSW452ec0273916478099c4716395e1bc18",  # Keyword: Classification category
        "Category:OSWd02741381aaa4709ae0753a0edc341ce",  # Enumeration
        "Category:OSW2c32802be59040248c85eda3479d484c",  # StatusEnumeration
        "Category:OSW9725d7a91bab4f1aa68f423e4e9bfcf4",  # TaskStatus (required for
        # Task/Kanban Board)
        "Item:OSWf474ec34b7df451ea8356134241aef8a",  # State:Done
        "Item:OSWa2b4567ad4874ea1b9adfed19a3d06d1",  # State:In work
        "Item:OSWaa8d29404288446a9f3ec7afa4e2a512",  # State:To do
        "Category:OSW65c8449bdd4f4fbcb7f68203a11d6e8f",  # Priority
        "Item:OSW8743c7d03c4e46c1bd42bb05e1a082d9",  # High
        "Item:OSW8d781c35212548fa9b2fccad3765da65",  # Medium
        "Item:OSWcaf7db070ad6407babc5245e84d76840",  # Low
        "Category:OSWe427aafafbac4262955b9f690a83405d",  # Tool
        "Category:Property",
        "Category:AnnotationProperty",
        "Category:ObjectProperty",
        "Category:DataProperty",
        "Category:QuantityProperty",
        "Category:OSW1b15ddcf042c4599bd9d431cbfdf3430",  # MainQuantityProperty
        "Category:OSW69f251a900944602a08d1cca830249b5",  # SubQuantityProperty
        # Entity and Category
        "Property:IsA",
        "Property:HasType",
        "Property:Display_title_of",
        "Property:SubClassOf",
        "Property:HasUuid",
        "Property:HasOswId",
        "Property:HasName",
        "Property:HasLabel",
        "Property:HasNormalizedLabel",
        "Property:Display title of lowercase",
        "Property:Display title of normalized",
        # "Property:HasAbbreviation", #ToDo: Multilang?
        "Property:HasDescription",
        "Property:HasImage",
        "Property:HasFileAttachment",
        "Property:HasPart",
        # Statements
        "Property:HasUnitSymbol",
        "Property:Corresponds to",
        # Process
        "Property:HasDate",
        "Property:HasStartDate",
        "Property:HasStartDateAndTime",
        "Property:HasEndDate",
        "Property:HasEndDateAndTime",
        "Property:HasInput",
        "Property:HasOutput",
        # Item
        "Property:Visible to",
        # "Property:HasTypicalProcess",  # used by tool
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
        "Template:Editor/Kanban",
        "Template:Viewer/Kekule",
        "Template:Viewer/Github/Code",
        "Module:Viewer/Github",  # requires Extension:ExternalData, Extension:WikiMarkdown
        "Template:Viewer/Link",
        "Module:Viewer/Link",
        "Template:Viewer/LinkAndEditButton",
        "Template:Viewer/Media",
        "Template:Viewer/File",  # to display files in tables
        "Module:Media",  # Note: refs some PNG files as examples, these should not be included
        "Template:Viewer/EditButton",  # inline edit in tables
    ],
)
# Provide the information needed (only) to create the page package
package_creation_config = WorldCreat(
    # Specify the path to the working directory - where the package is stored on disk
    working_dir=Path(__file__).parents[1] / "packages" / package_meta_data.repo,
    ignore_titles=[
        "File:OSWd8adafab997746e69864f23e7bfba734.png",  # example/test file
        "File:OSW5f36a59d4bb94ea0bf93f08f7470f609.png",  # example/test file
        "File:OSWd1c24f1c4b014ebe99c2a83672e3dfc7.png",  # example/test file
    ],
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
            #  read_listed_pages_from_script=True,
            #  script_dir=Path(__file__).parent,
        )
    )
