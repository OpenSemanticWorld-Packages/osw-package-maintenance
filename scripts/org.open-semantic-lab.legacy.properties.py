import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticLab"
package_repo = "org.open-semantic-lab.legacy"
package_id = "org.open-semantic-lab.legacy.properties"
package_name = "properties"
package_label = "OSL Legacy Properties"

working_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "packages",
    package_repo,
)


bundle = package.PagePackageBundle(
    publisher=f"{package_repo_org}",
    author=["Simon Stier"],
    language="en",
    publisherURL=f"https://github.com/{package_repo_org}/{package_repo}",
    packages={
        f"{package_name}": package.PagePackage(
            globalID=f"{package_id}",
            version="0.1.0",
            description="Provides core functionalities of OpenSemanticLab < 0.2.0",
            baseURL=f"https://raw.githubusercontent.com/{package_repo_org}/{package_repo}/main/{package_name}",
        )
    },
)

wtsite.create_page_package(
    package.PagePackageConfig(
        name=package_name,
        config_path=os.path.join(working_dir, f"{package_name}_packages.json"),
        bundle=bundle,
        titles=[
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
            "Property:Volume"
        ],
        skip_slot_suffix_for_main=True
    )
)
