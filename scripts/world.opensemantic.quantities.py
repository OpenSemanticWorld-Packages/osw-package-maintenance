import os
from pathlib import Path
from typing import Dict

from osw.auth import CredentialManager
from osw.core import OSW, AddOverwriteClassOptions, WtPage, WtSite
from reusable import WorldCreat, WorldMeta

from enriched_qudt import (
    ENRICHED_QUDT_PATH,
    load_enriched_qudt,
    get_unit_prefix_entities,
    get_quantity_unit_entities,
    get_quantitykind_and_characteristics,
    postprocess_jsondata_files,
)


# ---------------------------------------------------------------------------
# Main script
# ---------------------------------------------------------------------------

wtsite = WtSite(
    WtSite.WtSiteConfig(
        iri="wiki-dev.open-semantic-lab.org",
        cred_mngr=CredentialManager(
            cred_filepath=os.path.join(os.path.dirname(__file__), "accounts.pwd.yaml")
        ),
    )
)
osw_obj = OSW(site=wtsite)

# Load required schemas — ComposedUnit first to ensure full Item inheritance
osw_obj.fetch_schema(
    OSW.FetchSchemaParam(
        schema_title=[
            "Category:OSW6c2aea028a8647cd97f5d7c65c09cd44",  # ComposedUnit (must be first)
        ],
        mode="replace",
    )
)
osw_obj.fetch_schema(
    OSW.FetchSchemaParam(
        schema_title=[
            "Category:OSW99e0f46a40ca4129a420b4bb89c4cc45",  # Unit prefix
            "Category:OSWd2520fa016844e01af0097a85bb25b25",  # Quantity Unit
            "Category:OSW00fbd6feecb5408997ca18d4e681a131",  # Quantity Kind
            "Category:OSW4082937906634af992cf9a1b18d772cf",  # Quantity Value
            "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7",  # Fundamental Quantity Value Type
            "Category:OSWac07a46c2cf14f3daec503136861f5ab",  # Quantity Value Type
        ],
        mode="append",
    )
)

# Load enriched QUDT data
data = load_enriched_qudt(ENRICHED_QUDT_PATH)
print(f"Loaded enriched QUDT: {len(data['graph'])} items")

# Create entities
prefix_entities = get_unit_prefix_entities(data)
print(f"Created {len(prefix_entities)} UnitPrefix entities")

non_composed, composed, unit_id_to_osw_id = get_quantity_unit_entities(data)
print(f"Created {len(non_composed)} QuantityUnit + {len(composed)} ComposedUnit entities")

# Build unit entities map for QK creation
unit_entities_map = {}
for u in non_composed:
    osw_id = f"Item:OSW{str(u.uuid).replace('-', '')}"
    unit_entities_map[osw_id] = u
for u in composed:
    osw_id = f"Item:OSW{str(u.uuid).replace('-', '')}"
    unit_entities_map[osw_id] = u

qk_list, _, _ = get_quantitykind_and_characteristics(
    data, unit_id_to_osw_id, unit_entities_map
)
print(f"Created {len(qk_list)} QuantityKind entities")

entities_dict = {
    "prefixes": prefix_entities,
    "quantity_units": non_composed,
    "composed_prefix_quantity_units": composed,
    "quantity_kinds": qk_list,
}

pages: Dict[str, WtPage] = {}

for key, osw_obj_list in entities_dict.items():
    pages = {
        **pages,
        **osw_obj.store_entity(
            OSW.StoreEntityParam(
                entities=osw_obj_list,
                overwrite=AddOverwriteClassOptions.replace_remote,
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
    "Category:OSW6c2aea028a8647cd97f5d7c65c09cd44",  # "ComposedUnit"
    "Category:OSW00fbd6feecb5408997ca18d4e681a131",  # "Quantity Kind"
    "Category:OSW27782669526d4d9a8de83659c03c64d5",  # "System Of Quantities And Units"
    "Property:HasSymbol",
]
page_titles.extend(sorted(pages.keys()))

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    name="OSW Quantities",
    repo="world.opensemantic.quantities",
    id="world.opensemantic.quantities",
    subdir="base",
    branch="main",
    description=("Contains fundamental (physical) quantities, units and prefixes"),
    version="0.2.0",
    requiredPackages=[
        "world.opensemantic.core",
    ],
    author=["Andreas Räder", "Simon Stier", "Lukas Gold"],
    page_titles=page_titles,
)
package_creation_config = WorldCreat(
    working_dir=Path(__file__).parents[1] / "packages" / package_meta_data.repo,
    offline_pages=pages,
)

if __name__ == "__main__":
    package_meta_data.create(
        creation_config=package_creation_config,
    )
    postprocess_jsondata_files(package_creation_config.working_dir)
    package_meta_data.check_required_pages(
        params=WorldMeta.CheckRequiredPagesParams(
            creation_config=package_creation_config,
            read_listed_pages_from_script=False,
        )
    )
