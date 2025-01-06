from pathlib import Path
from typing import Dict

from reusable import WorldCreat, WorldMeta
import sys
import os
import pathlib
sys.path.append(str(pathlib.Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) / "tools" / "quantities-units" / "src" / "quantities-units"))
from main import update_local_osw, extract_data, transform_data, load_data
from osw.express import OswExpress
from osw.core import WtSite, WtPage, OSW, AddOverwriteClassOptions
from osw.utils.wiki import get_osw_id

osw_obj = OswExpress(
    domain="wiki-dev.open-semantic-lab.org",  # cred_filepath=pwd_file_path
)
#update_local_osw(osw_obj=osw_obj)

# I: Exctract Data
osw_ontology_instance = extract_data(debug=True)
# II: Transform Data
list_of_osw_obj_dict = transform_data(osw_ontology=osw_ontology_instance)

list_of_osw_obj_dict = {
    #"prefixes": list_of_osw_obj_dict["prefixes"],
    #"quanity_units": list_of_osw_obj_dict["quanity_units"],
    #"composed_prefix_quantity_units": list_of_osw_obj_dict["composed_prefix_quantity_units"],
    #"quantity_kinds": list_of_osw_obj_dict["quantity_kinds"],
    "fundamental_characteristics": list_of_osw_obj_dict["fundamental_characteristics"],
    "characteristics": list_of_osw_obj_dict["characteristics"],
}

pages: Dict[str, WtPage] = {}

for key, osw_obj_list in list_of_osw_obj_dict.items():
    
    # Define the namespace
    namespace = None
    meta_category_title = None
    if key == "fundamental_characteristics": 
        namespace = "Category"
        # MetaFundamentalQuantityValue
        meta_category_title = "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7"
    if key == "characteristics": 
        namespace = "Category"
        # MetaQuantityValue
        meta_category_title = "Category:OSWac07a46c2cf14f3daec503136861f5ab"    
        
    pages = {**pages, **osw_obj.store_entity(
        OSW.StoreEntityParam(
            entities=osw_obj_list,
            overwrite=AddOverwriteClassOptions.replace_remote,
            namespace=namespace,
            meta_category_title=meta_category_title,
            offline=True,
        )).pages}

# remove meta from jsondata since it's uuid is regenerated each time    
for p in pages.values():
    jd = p.get_slot_content("jsondata")
    if "meta" in jd:
        del jd["meta"]
    p.set_slot_content("jsondata", jd)
    
page_titles = [
    "Category:OSW4082937906634af992cf9a1b18d772cf", # "Quantity Value",
    #"Category:OSW7014422ed34957de9d4ca0fb6e3d74d3": "Page has no jsondata.",
    #"Category:OSW7468741a399c52338e44a8242cfed871": "Page has no jsondata.",
    #"Category:OSW76131090bf885b3b93394f5f4574e1a1": "Page has no jsondata.",
    "Category:OSWac07a46c2cf14f3daec503136861f5ab", # "Meta Quantity Value",
    "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7", # "Meta Fundamental Quantity Value",
]
page_titles.extend(list(pages.keys()))
    
# Provide information on the page package to be created
package_meta_data = WorldMeta(
    # Package name
    name="OSW Quantitive Characteristics",
    # Package repository name - usually the GitHub repository name
    repo="world.opensemantic.characteristics.quantitative",
    # Package ID - usually the same as repo
    id="world.opensemantic.characteristics.quantitative",
    # Package subdirectory - usually resembling parts of the package name
    subdir="base",
    # Package branch - usually "main"
    branch="main",
    # Provide a package description
    description=("Contains measureable qualitities based on (physical) quantities"),
    # Specify the package version - use semantic versioning
    version="0.1.0",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.quantities",
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
    working_dir=Path(__file__).parents[1]
    / "packages"
    / package_meta_data.repo,
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
            #script_dir=Path(__file__).parent,
        )
    )
