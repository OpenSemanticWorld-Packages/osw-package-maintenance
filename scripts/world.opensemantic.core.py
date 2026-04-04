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
    version="0.57.1",
    # Specify the required MediaWiki extensions
    requiredExtensions=["OpenSemanticLab", "ExternalData", "WikiMarkdown"],
    # Specify the required PagePackages
    requiredPackages=[],
    # Author(s)
    author=["Simon Stier", "Lukas Gold", "Andreas Räder"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Item:OSWf831ae62f2194f58a828b99ab406898b",  # OSW Core Package itself (manually updated for now)
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
        # Characteristics (merged from world.opensemantic.characteristics.basic)
        "Category:OSW93ccae36243542ceac6c951450a81d47",  # Characteristic
        "Category:OSWffe74f291d354037b318c422591c5023",  # CharacteristicType
        "Category:Item",
        "Category:OSW6ef70c808fb54abbbacb059c285713d4",  # OntologyRelated
        "Category:OSW31a9c96c1f444f84b944d49afbce409b",  # PagePackage
        "Category:OSWb24f37ada8d043c194e7036df5d86b39",  # UserGroup
        "Item:OSW5335efe7928d49619412fe28363b5e8a",  # Administrators
        "Item:OSW2b28cfd4bf8446e586f0e90152127b4a",  # RegisteredUsers
        "Category:OSW8b3e627eb76b46d68fce3a12ff220c8e",  # UserAccount
        "Category:OSW379d5a1589c74c82bc0de47938264d00",  # OwlThing
        "Category:OSW288260cd0728420c9f40ae1c5fa19111",  # Ontology
        "Category:OSW662db0a2ad0946148422245f84e82f64",  # OwlOntology
        "Category:OSW725a3cf5458f4daea86615fcbd0029f8",  # OwlClass
        "Category:OSW5f0dff1c477e45e7ad45e4e247e28f35",  # Documentation Extension
        "Category:OSW2ac4493f8635481eaf1db961b63c8325",  # Data
        "Category:OSWff333fd349af4f65a69100405a9e60c7",  # File
        "Category:OSW3e3f5dd4f71842fbb8f270e511af8031",  # LocalFile
        "Category:OSW05b244d0a669436e96fe4e1631d5a171",  # RemoteFile
        "Category:OSW11a53cdfbdc24524bf8ac435cbf65d9d",  # WikiFile => mwjson editor file upload schema
        # NOTE: Process, Task, PhysicalItem, Tool, Event, Status, Priority
        # categories + items moved to world.opensemantic.base
        "Category:OSWcbb09a36336740c6a2cd62db9bf647ec",  # IntangibleItem
        "Category:OSWa5812d3b5119416c8da1606cbe7054eb",  # DefinedTerm (moved from base)
        "Category:OSW09f6cdd54bc54de786eafced5f675cbe",  # Keyword
        "Item:OSW452ec0273916478099c4716395e1bc18",  # Keyword: Classification category
        "Category:OSWd02741381aaa4709ae0753a0edc341ce",  # Enumeration
        "Template:Query/SlotAction",
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
        "Property:HasSchema",
        "Property:Display_title_of",
        "Property:SubClassOf",
        "Property:HasUuid",
        "Property:HasOswId",
        "Property:HasName",
        "Property:HasLabel",
        "Property:HasNormalizedLabel",
        "Property:Display title of lowercase",
        "Property:Display title of normalized",
        "Property:HasStatement",
        # "Property:HasAbbreviation", #ToDo: Multilang?
        "Property:HasDescription",
        "Property:HasImage",
        "Property:HasFileAttachment",
        "Property:HasPart",
        # Statements
        "Property:HasUnitSymbol",
        "Property:Corresponds to",
        # NOTE: Process, Physical Item, Tool Properties moved to world.opensemantic.base
        # Item
        "Property:Visible to",
        # UserGroup and UserAccount
        "Property:HasGroupname",
        "Property:HasUsername",
        # PagePackage
        "Property:HasId",
        "Property:HasUrl",
        "Property:HasVersion",
        "Property:HasRange",  # Value range for ObjectProperty
        # Templates
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
    generate_package_documentation_page=True,
    generate_python_code=False,
    python_code_working_dir=Path(__file__).parents[1] / "python_packages" / "opensemantic.core-python" / "src" / "opensemantic" / "core",
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
