import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticWorld-Packages"
package_repo = "world.opensemantic.meta.docs"
package_id = "world.opensemantic.meta.docs.core"
package_name = "OSW Docs - Core"
package_subdir = "core"
package_branch = "main"

working_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "packages",
    package_repo,
)


bundle = package.PagePackageBundle(
    publisher=f"OpenSemanticWorld",
    author=["Simon Stier", "Lukas Gold"],
    language="en",
    publisherURL=f"https://github.com/{package_repo_org}/{package_repo}",
    packages={
        f"{package_name}": package.PagePackage(
            globalID=f"{package_id}",
            label=package_name,
            version="0.4.3",
            description="Provides core documentation of OpenSemanticWorld / -Lab",
            baseURL=f"https://raw.githubusercontent.com/{package_repo_org}/{package_repo}/{package_branch}/{package_subdir}/"
        )
    },
)

wtsite.create_page_package(
    package.PagePackageConfig(
        name=package_name,
        config_path=os.path.join(working_dir, f"packages.json"),
        content_path=os.path.join(working_dir, package_subdir),
        bundle=bundle,
        titles=[
            "Item:OSW70b4d6464c1d44a887eb86e3b39b8751", # StructedDataWorkshop
            "Item:OSWf1df064239044b8fa3c968339fb93344", # JsonTutorial
            "Item:OSWf4a9514baed04859a4c6c374a7312f10", # JsonSchemaTutorial
            "Item:OSW911488771ea449a6a34051f8213d7f2f", # JsonLdTutorial
            "Item:OSWee501c0fa6a9407d99c058b5ff9d55b4", # JsonApplicationTutorial
            "Item:OSW6df03625b42e4b44bd9f2dfa77387887", # HandlebarsTemplates
            "Item:OSW18201c9a18f64574a12d97efdeb2f953", # SchemaTemplateTutorial
            "Item:OSW7d3292e5104f45b1be4fc23901fae4fa", # TabularData
            "Item:OSW52c2c5a6bbc84fcb8eab0fa69857e7dc", # ArticleTutorial
            "Item:OSW7113f5cf921a4c82ad1872afeff9d01d", # TranscendWikitext
            "Item:OSWab674d663a5b472f838d8e1eb43e6784", # OswSchema
            "Item:OSW659a81662ff44af1b2b6febeee7c3a25", # OswPythonPackage
            #"Item:OSW92619b0700984fe7913e5fbbd7f194dc", # OswSpecialEditors
        ]
    )
)
