from pathlib import Path

from reusable import BigMapCreat, WorldMeta

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Batteries",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.batteries",
    # Package ID - usually the same as repo
    id="world.opensemantic.batteries",
    # Package subdirectory - usually resembling parts of the package name
    subdir="batteries",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=(
        "Provides battery specific items like ElectrochemicalTest, BatteryCell, etc."
    ),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Specify the required PagePackages
    requiredPackages=[
        # "world.opensemantic.base",
        # "world.opensemantic.lab"
    ],
    # Author(s)
    author=["Simon Stier", "Lukas Gold"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        # Missing pages as per script
        "Category:OSW0551abcd6f734047825e3ded4c8a0ffe",  # Page has no jsondata
        "Category:OSW51653bb12c534c0b92a255b0b5ca3984",  # Page has no jsondata
        "Category:OSW5a13eeda5ed5405ea7ef62ea6feeceec",  # Page has no jsondata
        "Category:OSW5eb9c52b804544dc870dfd54ff434428",  # Page has no jsondata
        # "Category:OSW8dd3cdf846b74e19943a5fff966f12c0",  # LFP battery cell test 2 of
        # # PE supplied",
        "Category:OSWc3d78c97659043f5abcf643513ae55e1",  # Page has no jsondata
        # "File:OSWaa635a571dfb4aa682e43b98937f5dd3.pdf",  # Hazard assessment of
        # # opening aged prismatic or pouch lithium-ion battery cells
        "Item:OSW5c23c534a3aa4fa6a4cf86d820277d27",  # LFP batch 0001
        "Property:Corresponds to",  # Page has no jsondata
        "Property:Visible to",  # Page has no jsondata
        # Recent changes
        "Item:OSW6a2406c5394a4a8a8ce1a2e1046b40fb",
        "Category:OSWb1428c1d948849eaa7bb50543a140a27",
        "Category:OSWdc59f9c4b99a415e96da5388b6b350e5",
        "Category:OSW712583f2479944deb2546b77cf860dda",
        "Item:OSWf52699c53f16430bb19a34f10a0fbc73",
        "Category:OSW7961ca50b89c4cd89cd102b4ce15566e",
        "Category:OSW54f5810625574f23ba20936ecad99f7e",
        "Category:OSWd5791d13ae43423ebb97ceb942c62d10",
        "Category:OSWcb952927097d43af8a498dbd09e8e89e",
        "Category:OSWf98f7a1c83f448a489429c3730e7b548",
        "Category:OSW0d44aad3c1d3467e82b483f27d814aad",
        "Category:OSWd7747cf501984e52bf7aa5e594068ccf",
        "Item:OSWc59647c3e3df4386aef45839f0a83aaa",
        "Category:OSW1a9524bf22384a9ebd7fed4b9b29e116",
        "Category:OSW56ab58326e0440e1a3f2086963325c44",
        "Category:OSW461473179c1a4ae297519477810f4172",
        "Property:HasDut",
        "Category:OSWc02165dc24544a10a2046b54506dedac",
        "Item:OSWb605c3b08b444fd0966f93e2edb5c602",
        "Category:OSWb869e525b25a4a9d8880a30075eb7d21",
        "Category:OSW0d5886c877304d038f10e1bcbb29d671",
        "Category:OSW02900397076740c3be51e5e190934d16",
        "Category:OSW37a57741ae2e4dd4b29b1172b6848be8",
        "Category:OSWf7528a256ea1428a8ac209605291a597",
        "Category:OSW401a0c32521642118f9e9b0076ab5720",
        "Category:OSWca99a9bb9ad24386b222d18a73c2af5e",
        "Category:OSW80c6929b1d74431890eb253ff8885223",
        "Category:OSW41bb92bc521a4ae1aaee29dc151f1ee3",
        "Item:OSWed11653b37424ef197a93a7fb893079d",
        "Category:OSW418d1402b35e4e099dd02a52a782bd47",
        "Category:OSW958399941fa64440bac1c0b7b572e57a",
        "Item:OSW15cf015b3199419684d3276d2d986d57",
        "Category:OSWfdebd62ed005495f915cd43aaced30c8",
        "Category:OSW822ee41305984fda91de275886fb1014",
        "Category:OSWe2837f8ca1884f6595a664f19fd7bf22",
        "Category:OSW1bab134ea1b14cba83f6ccdff9a39cb3",
        "Category:OSWf06c14937c164fae94e4343501ddc950",
        "Category:OSW8b48a5a4229145029265c000dc6ea483",
        "Category:OSW64f6635fd28044658c06f5a03bebb9d2",
        "Category:OSW0e56179ca32e49f4a92ddd71e0034550",
        "Item:OSW684cc2e12d0d4d0b804090f874eb487b",
        "Category:OSW6110d42bba33448b9a6348a3cd28b921",
        "Item:OSWbfbe148592884bd9a3586691737fb7ed",
        "Category:OSW6631a233da9747c098fd3394d7cd3d82",
        "Category:OSW199dfd892dd645659573268269161605",
        "Item:OSW4f8ee81010854ef38415a24860292df8",
        "Item:OSW447f2a13f55149088ca1ea9ab2060332",
        "Category:OSW63bf17f768ff4f0293b59d22f5953ec2",
        "Category:OSW71ee44ee83994cd891b0a535dac62461",
        "Category:OSW7e4ac258f8dd4d9ba03040da55ea8e73",
        "Category:OSWe69626f5804848fa978dbca65e6e084a",
        "Category:OSWa2c8dd387d0b4a0c807a5a7bde190ba3",
        "Category:OSW1e13562488954393ad21df1ea97b0b71",
        "Category:OSWe83096e2cb754dffb5d15b699e03d5c8",
        "Category:OSWa211cf52e86e47929768a769235f7144",
        "Item:OSW2280c83d9c704edba689da242e9076d5",
        "Item:OSW8da1aee5ded04434be9d8aa483d9996f",
        "Category:OSW4744375e811943b2a21e922cded383fc",
        "Category:OSW36082c03d48543aca08bfe4ea3afe8cb",
        "Category:OSW2cfa957f5e824cf38da52d547cebe73d",
        "Item:OSW315bf2e58ced496fa31acbf6a2940e52",
        "Item:OSWbcffb0953cef4cc4b9d3aa4edbf986fa",
        "Category:OSW26faea9125024fe08e98d4abbdf793a0",
        "Category:OSW9cbfca2e044940a9a2b336dfbdff0c47",
        "Category:OSW863e89704c0243a68749f747eaa9f3b6",
        "Category:OSW7de0f2441b724c3894093e3e35123fc8",
        "Category:OSW204337a832bf43c495905b3958e17223",
        "Category:OSWd0bea08c395c4ba4a269abbb994cb0b5",
        "Category:OSWc090fe6802cb471fa3d3dbc50bdc6c19",
        "Category:OSWa2c1702e240d49bb8fe1f7e1da74e161",
        "Category:OSW242d89e0188a4bbfaf0c47478af3a649",
        "Category:OSW0945915aa38b4ddd905bc959fed02320",
        "Category:OSW38ddea7b37fa4712858fe16404993b59",
        "Category:OSWa1a377f297f54ecabe558b46fb43ad02",
        "Category:OSWafcac83979f4472298b6acdc01981728",
        "Category:OSWad76c1ea5a6444a7980c287f2856d21e",
        "Category:OSW8c6de716ad66479a9b8bd6f786f6df6e",
        "Item:OSW982d9f062c4c4a7daca574edbf531bd8",
        "Category:OSW0c31c2d1182f41e1914a65f329aec378",
        "Category:OSWc07fc11ed51b4b2a9d62eec3127cd577",
        "Category:OSWb09db7a4bd8a404684e9223d75fb3537",
        "Category:OSW1cee2d62621f4d2f8477e9b336fa3262",
        "Category:OSW325fa42f96a94ba1ad96dbd1f62e0d6a",
        "Category:OSW807b7b36387a466a83bd08e30fe97b33",
        "Category:OSWd82bda461d474a5dbf274c8bd6f1cfcd",
        "Category:OSWffea76829cbc475eb518b19fd437c0d6",
        "Category:OSW670c84f7f7e64533a37081e6349bb008",
        "Category:OSW8f36767bb491449ebc959802c8d66d23",
        "Item:OSW274ebbb8e17b4e70947fdda1512c14be",
        "Category:OSW7d5c3e78685249f29b8bbed364e8373e",
        "Category:OSW4c3c3e060b134172bd8d1eac99be7a26",
        "Category:OSWb7e39094718840e291e931d113eca609",
        "Item:OSWaa8b905d0f084b9db1c7b7396d676586",
        "Item:OSWa73f6d6ce91d4a78a1132598a053baf9",
        "Category:OSW185651e8d17a478ea8a4a63dda3026bc",
        "Category:OSWfe8c9892fed6435586d9030886652151",
        "Category:OSWb5c76150935a4c009979330513ba3997",
        "Category:OSW39eb4428d105496bb4fd64e276b80cff",
        "Item:OSW517f9aa6ade2426895b1e439d56af04d",
        "Category:OSW02f14745aa5d40a08a2b7563b3ceff1a",
        "Category:OSW1ee1f5ccdb564f4e829b76b76028aa77",
        "Category:OSWc999a169d3a9474a89bbd7bcd0f4cc21",
        "Category:OSW182916df3eee472e88e7c8d114a7fe27",
        # Manual added
        "Main_Page",
        "Category:OSW680453b7563749a0a33f6be16036c81d",  # BatteryCell
        # "Category:OSW6f39d77241e24a33ab6d036dfac03ace",  # ElectrochemicalTest
        # "Category:OSWdda41d4a4ec0421babe0295c6edcb5df",  # ElectrochemicalTestProcedure
        "Category:OSWcb168c1ad3c7467bb4ed740381771928",  # CyclingTestProcedure
        # Batteries
        "Category:OSWe427aafafbac4262955b9f690a83405d",  # Tool
        "Category:OSWf0fe562f422d49c6877490b3dfee2f3f",  # Device
        "Category:OSWe0572f2791844010962886b892970b4d",  # Controlled Environment
        "Category:OSWb3b9ec5cb50d401c9b996ce3009b5c54",  # Environmental Test Chamber
        "Category:OSW43b7a7cf767c4c529ac260b117d19773",  # Climate Test Chamber
        "Category:OSW4ebd1194039943018ace13cd4c94774a",  # Temperature Test Chamber
        "Category:OSW5e3a5c9228ad4aec98830900e247ff39",  # Memmert
        # Peltier CooledIncubator
        "Category:OSWa36c243bd489400fb25857c1d9626383",  # Memmert IPP250plus
        "Category:OSW8355078074764a82bfddf43a25428a45",  # Vötsch Temperature Test
        # Chamber
        "Category:OSWaf33780e29a84867a6791555d23e8d5e",  # Vötsch VT 4021-S
        "Category:OSWf6f9f6c1c8f943909ffe681bca67252a",  # Glovebox
        "Category:OSW1849e7e9b69e445da44f50093a1d585b",  # MBRAUN Glovebox
        "Category:OSW85ab3eb019fb434aa7075ae6c008ede2",  # MB200MOD
        "Category:OSW69729530f3ca4addaf8dd95ea3781607",  # Electrochemical Testing
        # Device
        "Category:OSWef181c1daf2343fd8c132c39e7d748bd",  # Maccor Battery Tester
        "Category:OSWd5b87e52a61349dbb6077bf2447a7bf4",  # Maccor Series 4000
        # "Category:OSWe5aa96bffb1c4d95be7fbd46142ad203",  # Process
        # "Category:OSWfa0d5710bc0f45819b61b65fc4fd9656",  # Strict Participants Process
        "Category:OSW1a271f289649413488e2841580e43a45",  # Administrative Process
        # "Category:OSW3886740859ae459588fee73d3bb3c83e",  # Risk Assessment Process
        # "Category:OSW0e7fab2262fb4427ad0fa454bc868a0d",  # ElnEntry
        "Category:OSW47c67760dd164c82b570f58c8269b373",  # Post Mortem Experiment
        "Category:OSWafda1f2328804e3a89bf90f8af9c5527",  # Battery Cell Opening
        "Category:OSW6f39d77241e24a33ab6d036dfac03ace",  # Electrochemical Test
        "Category:OSWe21775c8dd604739885dfc24c32cc548",  # Procedure
        "Category:OSWdda41d4a4ec0421babe0295c6edcb5df",  # Electrochemical Test
        # Procedure
        "Category:OSWdda41d4a4ec0421babe0295c6edcb5df",  # Battery Test Procedure
        "Category:OSWbdb8b449342e4090b44b4f80c5ae9d92",  # Maccor Test Procedure
        "Category:OSW18f3251c2562407ea7bd7b19791b76f0",  # Bio-Logic Test Procedure
        "Category:OSW31ca9a739cb24079b36824045c0832aa",  # Material
        # "Category:OSW88894b63a51d46b08b5b4b05a6b1b3c3",  # Sample
        "Category:OSW0c3ab986534b44cf806a6f111094d61e",  # Battery Cell
        "Category:OSW9cf86699d6ba4b8c841a8e77e17a63ed",  # Material Type
        "Category:OSW0583b134c618484c9911a3dff145c7eb",  # Sample Type
        "Category:OSWb85e46ebb9ca4c83aac27e2c01dde369",  # Battery Cell Type
        "Category:TermNew" "Category:OSWa211cf52e86e47929768a769235f7144",  # Format
        "Category:OSWf04e73d3c3cb4e4ea7033066e472e9ff",  # Battery Cell Format
        # "Item:OSWd208bb6b47e1481c962cdc67975a2004",  # Coin Cell
        "Item:OSWd208bb6b47e1481c962cdc67975a2004",  # Cylindrical Cell
        "Item:OSW8d3a70c2a0c6486d81867be27dcff6db",  # Pouch Cell
        "Item:OSW5c944ba0f91e48878ff7df8525751747",  # Prismatic Cell
        # Core
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
        "JsonSchema:Meta",
        "Category:Category",
        "Category:Entity",
        "Category:Item",
        "Category:Term",
        "Category:OSW2ac4493f8635481eaf1db961b63c8325",  # Data
        "Category:OSWff333fd349af4f65a69100405a9e60c7",  # File
        "Category:OSW3e3f5dd4f71842fbb8f270e511af8031",  # LocalFile
        "Category:OSW05b244d0a669436e96fe4e1631d5a171",  # RemoteFile
        "Category:OSW11a53cdfbdc24524bf8ac435cbf65d9d",  # WikiFile
        "Category:OSWe5aa96bffb1c4d95be7fbd46142ad203",  # Process
        "Category:OSWc5d4829ed2744a219ba027171c75fa1d",  # Task
        "Category:OSWcbb09a36336740c6a2cd62db9bf647ec",  # IntangibleItem
        # "Category:OSWa5812d3b5119416c8da1606cbe7054eb",  # DefinedTerm (moved from base)
        "Category:OSW09f6cdd54bc54de786eafced5f675cbe",  # Keyword
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
        # "Category:OSWe427aafafbac4262955b9f690a83405d",  # Tool
        "Category:Property",
        "Category:AnnotationProperty",
        "Category:ObjectProperty",
        "Category:DataProperty",
        "Category:QuantityProperty",
        "Category:OSW1b15ddcf042c4599bd9d431cbfdf3430",  # MainQuantityProperty
        "Category:OSW69f251a900944602a08d1cca830249b5",  # SubQuantityProperty
        "Property:IsA",
        "Property:HasType",
        "Property:Display_title_of",
        "Property:SubClassOf",
        "Property:HasUuid",
        "Property:HasName",
        "Property:HasLabel",
        "Property:Display title of lowercase",
        "Property:Display title of normalized",
        "Property:HasDescription",
        "Property:HasImage",
        "Property:HasDate",
        "Property:HasStartDate",
        "Property:HasStartDateAndTime",
        "Property:HasEndDate",
        "Property:HasEndDateAndTime",
        "Property:HasUnitSymbol",
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
        "Template:Viewer/Media",
        "Template:Viewer/File",  # to display files in tables
        "Module:Media",
        # Base
        # "Category:OSW37a57741ae2e4dd4b29b1172b6848be8",  # PhysicalItem
        "Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26",  # Article
        "Category:OSW494f660e6a714a1a9681c517bbb975da",  # Tutorial
        "Category:OSW0e084decca6f48a7b023d6b7b2c1452d",  # Event
        "Category:OSW81e9e22e7d934382a6a56df7d3736957",  # Recipe
        "Category:OSWa5812d3b5119416c8da1606cbe7054eb",  # Term
        "Category:OSWfe72974590fd4e8ba94cd4e8366375e8",  # DataSet
        "Category:OSW3d238d05316e45a4ac95a11d7b24e36b",  # Location
        "Category:OSWd845b96813a344458f140e48c4d063fd",  # MetaDeviceCategory
        # "Category:OSWf0fe562f422d49c6877490b3dfee2f3f",  # Device
        "Category:OSWfa0d5710bc0f45819b61b65fc4fd9656",  # StrictParticipantsProcess
        # "Category:OSW1a271f289649413488e2841580e43a45",  # AdministrativeProcess
        "Category:OSW3886740859ae459588fee73d3bb3c83e",  # RiskAssessmentProcess ToDo: maybe to specific
        "Category:OSW02590972aeba46d7864ed492c0c11384",  # Host
        "Category:OSW77e749fc598341ac8b6d2fff21574058",  # Software
        "Category:OSW8c56fd1e858f499da801691c5f2b7309",  # WebService
        "Category:OSW473d7a1ed48544d1be83b258b5810948",  # Site
        "Category:OSW3cb8cef2225e403092f098f99bc4c472",  # OrganizationalUnit
        "Category:OSW44deaa5b806d41a2a88594f562b110e9",  # Person
        "Category:OSWd9aa0bca9b0040d8af6f5c091bf9eec7",  # User
        "Category:OSWb2d7e6a2eff94c82b7f1f2699d5b0ee3",  # Project
        "Category:OSWd22af0aa3b00462a9da9b509538e8926",  # FundingCall
        "Category:OSW4bcd4a99a73f482ea40ac4210dfab836",  # Building
        "Category:OSW6c4212f1a39342be963d2b9efd19c5c2",  # Floor
        "Category:OSWc5ed0ed1e33c4b31887c67af25a610c1",  # Room
        "Category:OSWac9f0e49d8024804bd7d77058322a3fe",  # RoomUsage
        "Category:OSWae92be81cdb34d22844d4791ef790d93",  # AreaUsageType
        "Category:OSW1969007d5acf40539642877659a02c23",  # Organization
        "Category:OSWcffdc90247c142eca7f23ab6c69e49a1",  # NonGovernmentalOrganization
        "Category:OSWd9521d3054814dd29c2bcdbd9185d1f0",  # Association
        "Category:OSW5f4a3751d23e482d80fb0b72dcd6bc31",  # Corporation
        "Category:OSWd7085ef89b0e4a69ac4f2d28bda2d2c0",  # Foundation
        "Category:OSW11ee14fb9f774b4b89bdb9bb89aac14d",  # University
        "Category:OSWfe3e842b804445c7bb0dd8ee61da2d70",  # OrganizationalSubUnit
        "Category:OSW94aa074255374580b70337340c5ccc1b",  # Department
        "Category:OSWa01126bc9e9048988cb0f49e359015bc",  # Faculty
        "Category:OSWb8b6278763d54b0784eea9d3b3d183a4",  # Group
        "Category:OSW5427361692374c8eaa6bd3733b92d343",  # Institute
        "Category:OSW5efde23b1d8c4e1c864ef039cb0616ed",  # PersonRole
        "Category:OSW07a0faef5be94b788514a2dd5dca20bf",  # BuildingFunction
        "Category:OSW973a5cd08ea14524a57089f0b3c9c6ff",  # Requirement
        "Item:OSWab093fd8af104a49882704cea3bbaf7b",  # FunctionalRequirement
        "Item:OSWbb07a72940554b1b978c44e5db4bd314",  # NonFunctionalRequirement
        "Template:Editor/Requirements",
        "Property:HasId",
        "Property:IsRelatedTo",
        "Property:HasPhoneNumber",
        "Property:HasApprover",
        "Property:HasOrderer",
        "Property:HasContact",
        "Property:HasUrl",
        "Property:HasVersion",
        "Property:HasManufacturer",
        "Property:HasManual",
        # "Property:HasPurpose",
        "Property:HasResponsiblePerson",
        "Property:IsLocatedIn",
        "Property:HasDepartment",
        # "Property:HasDatabase",
        "Property:HasInventoryNumber",
        # "Property:HasMeasurementChannels",
        "Property:HasRiskAssessment",
        "Property:HasOwner",
        "Property:HasSerialNumber",
        "Property:HasNetworkDomain",
        "Property:HasIp4Address",
        # Lab
        # "Category:OSW31ca9a739cb24079b36824045c0832aa",  # Material
        # "Category:OSW0583b134c618484c9911a3dff145c7eb",  # ChemicalCompound
        "Category:OSW88894b63a51d46b08b5b4b05a6b1b3c3",  # Sample
        "Category:OSW29f0a4619cc243679e68b682d3bdb890",  # GeoSample
        "Category:OSW0e7fab2262fb4427ad0fa454bc868a0d",  # ElnEntry
        "Category:OSWda27e2fff10848ebb728ffb69c49a16d",  # DataTool"
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
package_creation_config = BigMapCreat(  # WorldCreat(
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
