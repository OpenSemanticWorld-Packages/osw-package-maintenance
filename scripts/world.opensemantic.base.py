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
    version="0.17.13",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.core",
    ],
    # Author(s)
    author=["Simon Stier", "Lukas Gold", "Matthias Albert Popp", "Alexander Triol"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        # "Category:OSW37a57741ae2e4dd4b29b1172b6848be8",  # PhysicalItem
        "Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26",  # Article
        "Category:OSW494f660e6a714a1a9681c517bbb975da",  # Tutorial
        "Category:OSW0e084decca6f48a7b023d6b7b2c1452d",  # Event
        "Category:OSW81e9e22e7d934382a6a56df7d3736957",  # Recipe
        "Category:OSWa5812d3b5119416c8da1606cbe7054eb",  # Term
        "Category:OSWfe72974590fd4e8ba94cd4e8366375e8",  # DataSet
        "Category:OSW3d238d05316e45a4ac95a11d7b24e36b",  # Location
        "Category:OSWd845b96813a344458f140e48c4d063fd",  # MetaDeviceCategory
        "Category:OSWf0fe562f422d49c6877490b3dfee2f3f",  # Device
        "Category:OSWfa0d5710bc0f45819b61b65fc4fd9656",  # StrictParticipantsProcess
        "Category:OSW1a271f289649413488e2841580e43a45",  # AdministrativeProcess
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
