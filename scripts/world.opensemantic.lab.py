import os

import osw.model.page_package as package
from osw.wtsite import WtSite

pwd_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "accounts.pwd.yaml"
)

wtsite = WtSite.from_domain("wiki-dev.open-semantic-lab.org", pwd_file_path)

package_repo_org = "OpenSemanticWorld-Packages"
package_repo = "world.opensemantic.lab"
package_id = "world.opensemantic.lab"
package_name = "OSW Lab"
package_subdir = "base"
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
            version="0.2.1",
            description="For material science, etc.",
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
            #"Property:HasMassConcentration",
            "Category:OSW31ca9a739cb24079b36824045c0832aa", # Material
            "Category:OSW0583b134c618484c9911a3dff145c7eb", # ChemicalCompound
            "Category:OSW88894b63a51d46b08b5b4b05a6b1b3c3", # Sample
            "Category:OSW29f0a4619cc243679e68b682d3bdb890", # GeoSample
            "Category:OSW0e7fab2262fb4427ad0fa454bc868a0d", # ElnEntry
        ]
    )
)
