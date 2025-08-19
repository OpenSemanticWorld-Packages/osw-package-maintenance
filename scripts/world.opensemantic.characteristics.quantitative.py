import os
import pathlib
import pickle
import re
import sys
from pathlib import Path
from typing import Dict

import osw

# from osw.express import OswExpress
from osw.auth import CredentialManager
from osw.core import OSW, AddOverwriteClassOptions, OverwriteOptions, WtPage, WtSite
from osw.utils.wiki import get_osw_id
from quantities_units.main import (
    create_smw_quantity_properties,
    extract_data,
    load_data,
    transform_data,
    update_local_osw,
)
from reusable import WorldCreat, WorldMeta

# osw_obj = OswExpress(
#    domain="wiki-dev.open-semantic-lab.org",  # cred_filepath=pwd_file_path
# )
wtsite = WtSite(
    WtSite.WtSiteConfig(
        iri="wiki-dev.open-semantic-lab.org",
        cred_mngr=CredentialManager(
            cred_filepath=os.path.join(os.path.dirname(__file__), "accounts.pwd.yaml")
        ),
    )
)
osw_obj = OSW(site=wtsite)

# update_local_osw(osw_obj=osw_obj) # note: this fails in debugging mode due to working directory not being set correctly

cache = True
cache = False
cache_file = Path(__file__).parent / "list_of_osw_obj_dict.pickle"

if cache:
    # load pickle file
    with open(cache_file, "rb") as f:
        list_of_osw_obj_dict = pickle.load(f)

else:

    # I: Exctract Data
    osw_ontology_instance = extract_data(debug=True)
    # II: Transform Data
    list_of_osw_obj_dict = transform_data(osw_ontology=osw_ontology_instance)

    # dump pickle file
    with open(cache_file, "wb") as f:
        pickle.dump(list_of_osw_obj_dict, f)

quantity_property_entitites = create_smw_quantity_properties(
    list_of_osw_obj_dict=list_of_osw_obj_dict
)
p_entities = list(quantity_property_entitites.values())

# list_of_osw_obj_dict["fundamental_characteristics"]["Category:OSWee9c7e5c343e542cb5a8b4648315902f"], # Length
# list_of_osw_obj_dict["characteristics"]["Category:OSW24275b1c56ea58dcae38c44409251a64"], # Diameter

# filter fundamental_characteristics and characteristics by name "Length" and "Diameter"
c_entities = [
    x for x in list_of_osw_obj_dict["fundamental_characteristics"] if x.name == "Length"
]
c_entities += [
    x for x in list_of_osw_obj_dict["characteristics"] if x.name == "Diameter"
]
c_entities += [x for x in list_of_osw_obj_dict["characteristics"] if x.name == "Height"]
c_entities += [x for x in list_of_osw_obj_dict["characteristics"] if x.name == "Width"]

# p_entities = [
#     quantity_property_entitites["Property:HasLengthValue"],
#     quantity_property_entitites["Property:HasDiameterValue"],
#     quantity_property_entitites["Property:HasHeightValue"],
#     quantity_property_entitites["Property:HasWidthValue"],
# ]
# print(p_entities)
# osw_obj.store_entity( OSW.StoreEntityParam(entities=c_entities[0], overwrite=AddOverwriteClassOptions.replace_remote, namespace="Category", meta_category_title = "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7" ) )
# osw_obj.store_entity( OSW.StoreEntityParam(entities=c_entities[1:4], overwrite=AddOverwriteClassOptions.replace_remote, namespace="Category",  meta_category_title = "Category:OSWac07a46c2cf14f3daec503136861f5ab" ) )
# osw_obj.store_entity( OSW.StoreEntityParam(entities=p_entities, overwrite=AddOverwriteClassOptions.replace_remote,) )

list_of_osw_obj_dict = {
    # "prefixes": list_of_osw_obj_dict["prefixes"],
    # "quanity_units": list_of_osw_obj_dict["quanity_units"],
    # "composed_prefix_quantity_units": list_of_osw_obj_dict["composed_prefix_quantity_units"],
    # "quantity_kinds": list_of_osw_obj_dict["quantity_kinds"],
    "fundamental_characteristics": list_of_osw_obj_dict["fundamental_characteristics"],
    "characteristics": list_of_osw_obj_dict["characteristics"],
    "properties": p_entities,
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
    "Category:OSW4082937906634af992cf9a1b18d772cf",  # "Quantity Value",
    # "Category:OSW7014422ed34957de9d4ca0fb6e3d74d3": "Page has no jsondata.",
    # "Category:OSW7468741a399c52338e44a8242cfed871": "Page has no jsondata.",
    # "Category:OSW76131090bf885b3b93394f5f4574e1a1": "Page has no jsondata.",
    "Category:OSWac07a46c2cf14f3daec503136861f5ab",  # "Quantity Value Type",
    "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7",  # "Fundamental Quantity Value Type",
]
page_titles.extend(list(pages.keys()))

# Generate python module
# copy _model_generated.py to _model_py
# cut and past 'Characteristic' and 'QuantityValue' classes to _static.py (update existing classes)
# replace 'class PropertyType\(str, Enum\):((\r\n|\r|\n)[\s\S]*)UnitPrefix.update_forward_refs\(\)' with '' (remove core schemas)
# replace '$\textit' with '$\\textit'
# replace ' \underline with ' \\underline' and '$\underline with '$\\underline'
# replace '^from [\s\S]*?(\r\n|\r|\n)' with '' (remove all imports)
# replace '^# [\s\S]*?(\r\n|\r|\n)' with '' (remove all comments)
# replace '^(\r\n|\r|\n){3,}' with '\n\n' (remove multiple empty lines)
# replace '(Enum' with '(UnitEnum'
# replace 'DimensionlessUnit._field' with 'DimensionlessUnit.dimensionless'
# past imports at head of file:
# from opensemantic.characteristics.quantitative._static import QuantityValue, UnitEnum
# from typing import Any, Optional
# from pydantic.v1 import Field

result_model_path = (
    Path(__file__).parent.parent
    / "python_packages"
    / "opensemantic.characteristics.quantitative-python"
    / "src"
    / "opensemantic"
    / "characteristics"
    / "quantitative"
    / "_model_generated.py"
)
# for i, p in enumerate(pages.values()):
#     if i > 1:
#         break
#     print(f"{i}: {p.title} ({p.get_slot_content('jsonschema')})")
# osw_obj.fetch_schema(fetchSchemaParam=OSW.FetchSchemaParam(
#     schema_title=page_titles[:10000],
#     offline_pages=pages,
#     #result_model_path=Path(__file__).parent / "generated" / "schema.py",
#     result_model_path=result_model_path,
#     #mode="replace",
#     mode="replace"
# ))

# # open result model path and remove repeating code
# pattern = r"""
#     ^\#\s*generated\s+by\s+datamodel-codegen:.*\n      # Match '# generated by datamodel-codegen:' line
#     ^\#\s*filename:.*\n                                # Match '# filename:' line
#     (?:\n)*                                            # Match any number of empty lines
#     (?:from\s+\S+\s+import\s+.*\n)+                    # Match one or more 'from ... import ...' lines
# """

# # Compile the regex
# regex = re.compile(pattern, flags=re.MULTILINE | re.VERBOSE)

# # Read the content of the file
# with open(result_model_path, 'r') as file:
#     content = file.read()
# # Remove the matched block
# new_content = regex.sub('', content)
# # Write the modified content back to a file
# with open(result_model_path, 'w') as file:
#     file.write(new_content)

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
    version="0.2.2",
    # Specify the required PagePackages
    requiredPackages=[
        "world.opensemantic.quantities",
    ],
    # Author(s)
    author=["Andreas Räder", "Matthias Albert Popp", "Simon Stier"],
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
