import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticWorld-Packages"
package_repo = "world.opensemantic.lab.virtual"
package_id = "world.opensemantic.lab.virtual"
package_name = "OSW Virtual Lab"
package_subdir = "base"
package_branch = "main"

working_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "packages",
    package_repo,
)


bundle = package.PagePackageBundle(
    publisher=f"OpenSemanticWorld",
    author=["Simon Stier", "Andreas Räder"],
    language="en",
    publisherURL=f"https://github.com/{package_repo_org}/{package_repo}",
    packages={
        f"{package_name}": package.PagePackage(
            globalID=f"{package_id}",
            label=package_name,
            version="0.2.0",
            description="For modelling, simulation and optimization",
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
            "Category:OSW8e511130cecf4d7fa4177c9c65904fc1", # Model
            "Category:OSWecff4345b4b049218f8d6628dc2f2f21", # MetaModel
            "Category:OSW553f78cc66194ae1873241207b906c4b", # BattmoModel
        ]
    )
)
