import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticWorld-Packages"
package_repo = "world.opensemantic.demo"
package_id = "world.opensemantic.demo.common"
package_name = "OSW Demo - Common"
package_subdir = "common"
package_branch = "main"

working_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "packages",
    package_repo,
)


bundle = package.PagePackageBundle(
    publisher=f"OpenSemanticWorld",
    author=["Simon Stier"],
    language="en",
    publisherURL=f"https://github.com/{package_repo_org}/{package_repo}",
    packages={
        f"{package_name}": package.PagePackage(
            globalID=f"{package_id}",
            label=package_name,
            version="0.2.0",
            description="Provides common demo content",
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
            "Zentrales_Wiki/Landing_page_v2", 
            "Item:OSWb894a0c0e11c47d8a0dc591f75c7962c", # TowardsAnOpenSemanticWorld
            "Item:OSW0e49b7ed40774f0a9788158794cb88cf", # FemsEuromat2023
            "Item:OSW3a941905208445c2ae5d181646a87de2", # Porridge
            "Item:OSWea3abf8df16940ba87dc7b68ddcf6e34", # DemoArticle
            "Item:OSW43b7ce95da134566bc69f221442cfd18", # DemoProject
            "Item:OSW727ae933ec6d48f18e637e8ffe15e436", # DemoElnEntry
            "Item:OSW8ec5338887b04936869798218254c1e7", # DemoUser
            "Item:OSWe0dc3ee6559648659238b9dd4372cb8f", # Benzene
        ]
    )
)
