import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticWorld-Packages"
package_repo = "world.opensemantic.base"
package_id = "world.opensemantic.base"
package_name = "OSW Base"
package_subdir = "base"
package_branch = "main"

working_dir = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "packages",
    package_repo,
)


bundle = package.PagePackageBundle(
    publisher=f"OpenSemanticWorld",
    author=["Simon Stier", "Lukas Gold", "Alexander Triol"],
    language="en",
    publisherURL=f"https://github.com/{package_repo_org}/{package_repo}",
    packages={
        f"{package_name}": package.PagePackage(
            globalID=f"{package_id}",
            label=package_name,
            version="0.7.0",
            description="Provides base items like Article, Person, Project",
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
            "Category:OSW92cc6b1a2e6b4bb7bad470dfdcfdaf26", # Article
            "Category:OSW494f660e6a714a1a9681c517bbb975da", # Tutorial
            "Category:OSW0e084decca6f48a7b023d6b7b2c1452d", # Event
            "Category:OSW81e9e22e7d934382a6a56df7d3736957", # Recipe
            "Category:OSWa5812d3b5119416c8da1606cbe7054eb", # Term
            "Category:OSW57beed5e1294434ba77bb6516e461456", # EmmoTerm
            #"Category:OSW2ac4493f8635481eaf1db961b63c8325", # Data
            #"Category:OSWfe72974590fd4e8ba94cd4e8366375e8", # DataSet
            #"Category:OSWff333fd349af4f65a69100405a9e60c7", # File
            "Category:OSW3d238d05316e45a4ac95a11d7b24e36b", # Location
            "Category:OSW473d7a1ed48544d1be83b258b5810948", # Site
            "Category:OSW3cb8cef2225e403092f098f99bc4c472", # OrganizationalUnit
            "Category:OSW44deaa5b806d41a2a88594f562b110e9", # Person
            "Category:OSWd9aa0bca9b0040d8af6f5c091bf9eec7", # User
            "Category:OSWb2d7e6a2eff94c82b7f1f2699d5b0ee3", # Project


        ]
    )
)
