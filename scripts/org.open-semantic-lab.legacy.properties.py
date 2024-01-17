from pathlib import Path

from reusable import OslCreat, OslMeta

# Provide information on the page package to be created
package_meta_data = OslMeta(
    # Package name
    name="OSL Legacy Properties",
    # Package repository name - usually the GitHub repository name
    repo="org.open-semantic-lab.legacy",
    # Package ID - usually the same as repo
    id="org.open-semantic-lab.legacy.properties",
    # Package subdirectory - usually resembling parts of the package name
    subdir="properties",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Provides core functionalities of OpenSemanticLab < 0.2.0"),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Specify the required PagePackages
    requiredPackages=[],
    # Author(s)
    author=["Simon Stier"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=[
        "Property:HasAbbreviation",
        "Property:HasAbstract",
        "Property:HasAccessory",
        "Property:HasAdditionalDocument",
        "Property:HasAlternativeNames",
        "Property:HasAmbientPressure",
        "Property:HasAnodeMass",
        "Property:HasBusinessUnit",
        "Property:HasCas",
        "Property:HasChEBIID",
        "Property:HasChemicalStructureSDS",
        "Property:HasCompetence",
        "Property:HasConstructionYear",
        "Property:HasCoordinates",
        "Property:HasCreationDate",
        "Property:HasCreator",
        "Property:HasDatasheet",
        "Property:HasDate",
        "Property:HasDensityComment",
        "Property:HasDepartment",
        "Property:HasDescription",
        "Property:HasDeviceType",
        "Property:HasDeviceTypeName",
        "Property:HasDimensionlessRatio",
        "Property:HasDisplayName",
        "Property:HasDuration",
        "Property:HasElectrodeMass",
        "Property:HasEmail",
        "Property:HasEndDate",
        "Property:HasEndDateAndTime",
        "Property:HasFaxNumber",
        "Property:HasFirstName",
        "Property:HasFloor",
        "Property:HasFloorCount",
        "Property:HasForce",
        "Property:HasForcePerArea",
        "Property:HasFullName",
        "Property:HasGender",
        "Property:HasGrantor",
        "Property:HasHazardStatement",
        "Property:HasHazardStatementComment",
        "Property:HasHazardWarning",
        "Property:HasHouseNumber",
        "Property:HasId",
        "Property:HasImage",
        "Property:HasInput",
        "Property:HasInputUnitSymbol",
        "Property:HasInstitution",
        "Property:HasKeyword",
        "Property:HasLength",
        "Property:HasLiquidVolume",
        "Property:HasLongName",
        "Property:HasMailingList",
        "Property:HasManager",
        "Property:HasManual",
        "Property:HasManufacturer",
        "Property:HasManufacturerTypeId",
        "Property:HasMass",
        "Property:HasMember",
        "Property:HasMobilePhoneNumber",
        "Property:HasMoleFraction",
        "Property:HasMonetaryValue",
        "Property:HasName",
        "Property:HasNumber",
        "Property:HasNumberOfEntities",
        "Property:HasObject",
        "Property:HasOntologyIri",
        "Property:HasOtsBase64",
        "Property:HasOuHead",
        "Property:HasOuHeadDeputy",
        "Property:HasOuName",
        "Property:HasOuNumber",
        "Property:HasOutput",
        "Property:HasParameter",
        "Property:HasPart",
        "Property:HasParticipant",
        "Property:HasPartner",
        "Property:HasPhoneNumber",
        "Property:HasPostalCode",
        "Property:HasPrecautionaryStatementCode",
        "Property:HasPredecessor",
        "Property:HasPressure",
        "Property:HasProject",
        "Property:HasProposal",
        "Property:HasPubChemCid",
        "Property:HasPubChemID",
        "Property:HasReceiptDate",
        "Property:HasReport",
        "Property:HasResponsiblePerson",
        "Property:HasRiskAssessment",
        "Property:HasRole",
        "Property:HasRoom",
        "Property:HasRoomFunction",
        "Property:HasRoomNumber",
        "Property:HasRoomUsageType",
        "Property:HasSecretary",
        "Property:HasSerialNumber",
        "Property:HasSha256",
        "Property:HasSigmaCostCenter",
        "Property:HasSigmaOu",
        "Property:HasStartDate",
        "Property:HasStartDateAndTime",
        "Property:HasStatus",
        "Property:HasStreet",
        "Property:HasStress",
        "Property:HasSubordinateOu",
        "Property:HasSubType",
        "Property:HasSuccessor",
        "Property:HasSuperordinateOu",
        "Property:HasSurname",
        "Property:HasTargetStatus",
        "Property:HasTemperature",
        "Property:HasTestQuantity",
        "Property:HasThermodynamicTemperature",
        "Property:HasTime",
        "Property:HasTool",
        "Property:HasTopic",
        "Property:HasType",
        "Property:HasUnitDefinition",
        "Property:HasUnitSymbol",
        "Property:HasUrl",
        "Property:HasUsername",
        "Property:HasUuid",
        "Property:HasVolume",
        "Property:HasWaveLength",
        "Property:HasWikiDataId",
        "Property:HasYear",
        "Property:HasYearLabel",
        "Property:IsA",
        "Property:IsDisplayUnit",
        "Property:IsInputUnit",
        "Property:IsInstanceOf",
        "Property:IsLocatedIn",
        "Property:IsObjectParameterOf",
        "Property:IsOutputOf",
        "Property:IsPartOf",
        "Property:IsRelatedTo",
        "Property:IsSubprocessOf",
        "Property:Number",
        "Property:Position",
        "Property:Volume",
    ],
)
# Provide the information needed (only) to create the page package
package_creation_config = OslCreat(
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


# todo: check if the following deviating lines are needed:
# baseURL = f"https://raw.githubusercontent.com/{package_repo_org}/{package_repo}/main/
#   {package_name}",
# config_path = os.path.join(working_dir, f"{package_name}_packages.json"),
