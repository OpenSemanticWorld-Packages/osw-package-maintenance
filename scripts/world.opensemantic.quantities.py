import os
import pathlib
import sys
from calendar import c
from pathlib import Path
from typing import Dict

from reusable import WorldCreat, WorldMeta

sys.path.append(
    str(
        pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        / "tools"
        / "quantities-units"
        / "src"
        / "quantities-units"
    )
)
from osw.core import OSW, AddOverwriteClassOptions, WtPage, WtSite
from osw.express import OswExpress
from osw.utils.wiki import get_osw_id
from quantities_units.main import (
    extract_data,
    load_data,
    transform_data,
    update_local_osw,
)

osw_obj = OswExpress(
    domain="wiki-dev.open-semantic-lab.org",  # cred_filepath=pwd_file_path
)
# update_local_osw(osw_obj=osw_obj)

# I: Exctract Data
osw_ontology_instance = extract_data(debug=True)
# II: Transform Data
list_of_osw_obj_dict = transform_data(osw_ontology=osw_ontology_instance)

list_of_osw_obj_dict = {
    "prefixes": list_of_osw_obj_dict["prefixes"],
    "quanity_units": list_of_osw_obj_dict["quanity_units"],
    "composed_prefix_quantity_units": list_of_osw_obj_dict[
        "composed_prefix_quantity_units"
    ],
    "quantity_kinds": list_of_osw_obj_dict["quantity_kinds"],
    # "fundamental_characteristics": list_of_osw_obj_dict["fundamental_characteristics"],
    # "characteristics": list_of_osw_obj_dict["characteristics"],
}

pages: Dict[str, WtPage] = {}

for key, osw_obj_list in list_of_osw_obj_dict.items():

    # Define the namespace
    namespace = None
    meta_category_title = None
    if key == "fundamental_characteristics":
        namespace = "Category"
        # FundamentalQuantityValueType
        meta_category_title = "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7"
    if key == "characteristics":
        namespace = "Category"
        # QuantityValueType
        meta_category_title = "Category:OSWac07a46c2cf14f3daec503136861f5ab"

    pages = {
        **pages,
        **osw_obj.store_entity(
            OSW.StoreEntityParam(
                entities=osw_obj_list,
                overwrite=AddOverwriteClassOptions.replace_remote,
                namespace=namespace,
                meta_category_title=meta_category_title,
                offline=True,
            )
        ).pages,
    }

# remove meta from jsondata since it's uuid is regenerated each time
for p in pages.values():
    jd = p.get_slot_content("jsondata")
    if "meta" in jd:
        del jd["meta"]
    p.set_slot_content("jsondata", jd)

page_titles = [
    "Category:OSW99e0f46a40ca4129a420b4bb89c4cc45",  # "Unit prefix"
    "Category:OSWd2520fa016844e01af0097a85bb25b25",  # "Quantity Unit"
    "Category:OSW268cc84d3dff4a7ba5fd489d53254cb0",  # "Composed Quantity Unit with Unit Prefix"
    "Category:OSW00fbd6feecb5408997ca18d4e681a131",  # "Quantity Kind"
    "Property:HasSymbol",
]
page_titles.extend(list(pages.keys()))

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Quantities",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.quantities",
    # Package ID - usually the same as repo
    id="world.opensemantic.quantities",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Contains fundamental (physical) quantities, units and prefixes"),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.characteristics.basic",
    ],
    # Author(s)
    author=["Andreas Räder", "Simon Stier"],
    # List the full page titles of the pages to be included in the package
    # You can include a comment in the same line, stating the page label
    page_titles=page_titles,
)
# Provide the information needed (only) to create the page package
package_creation_config = WorldCreat(
    # Specify the path to the working directory - where the package is stored on disk
    working_dir=Path(__file__).parents[1] / "packages" / package_meta_data.repo,
    offline_pages=pages,
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
            read_listed_pages_from_script=False,
            # script_dir=Path(__file__).parent,
        )
    )
