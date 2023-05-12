import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticWorld-Packages"
package_repo = "world.opensemantic.core"
package_id = "world.opensemantic.core"
package_name = "OSW Core"
package_subdir = "core"
package_branch = "main"

working_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "packages",
    package_repo,
)

bundle = package.PagePackageBundle(
    publisher="OpenSemanticWorld",
    author=["Simon Stier"],
    language="en",
    publisherURL=f"https://github.com/{package_repo_org}/{package_repo}",
    packages={
        f"{package_name}": package.PagePackage(
            globalID=f"{package_id}",
            label=package_name,
            version="0.13.0",
            description="Provides core functionalities of OpenSemanticWorld / OpenSemanticLab",
            baseURL=f"https://raw.githubusercontent.com/{package_repo_org}/{package_repo}/{package_branch}/{package_subdir}/",
        )
    },
)

wtsite.create_page_package(
    package.PagePackageConfig(
        name=package_name,
        config_path=os.path.join(working_dir, "packages.json"),
        content_path=os.path.join(working_dir, package_subdir),
        bundle=bundle,
        titles=[
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
            "Category:OSW2ac4493f8635481eaf1db961b63c8325", # Data
            #"Category:OSWfe72974590fd4e8ba94cd4e8366375e8", # DataSet
            "Category:OSWff333fd349af4f65a69100405a9e60c7", # File
            "Category:OSW11a53cdfbdc24524bf8ac435cbf65d9d", # WikiFile
            "Category:OSWe5aa96bffb1c4d95be7fbd46142ad203", # Process 
            "Category:OSWe427aafafbac4262955b9f690a83405d", # Tool
            "Category:Property",
            "Category:ObjectProperty",
            "Category:QuantityProperty",
            "Category:OSW1b15ddcf042c4599bd9d431cbfdf3430", # MainQuantityProperty
            "Category:OSW69f251a900944602a08d1cca830249b5", # SubQuantityProperty
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
)
