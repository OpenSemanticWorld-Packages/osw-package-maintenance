import os
import pickle
import uuid as uuid_module
from logging import warning
from pathlib import Path
from typing import Dict

from osw.auth import CredentialManager
from osw.core import OSW, AddOverwriteClassOptions, WtPage, WtSite
from reusable import WorldCreat, WorldMeta

from enriched_qudt import (
    ENRICHED_QUDT_PATH,
    _make_uuid,
    load_enriched_qudt,
    get_unit_prefix_entities,
    get_quantity_unit_entities,
    get_quantitykind_and_characteristics,
    postprocess_jsondata_files,
)


def create_smw_quantity_properties(entities_dict: dict):
    """Create SMW Quantity Properties from entities_dict."""
    from osw.model import entity as model

    entity_map = {}
    ns_map = {
        "fundamental_characteristics": "Category",
        "characteristics": "Category",
        "quantity_kinds": "Item",
        "quantity_units": "Item",
        "composed_prefix_quantity_units": "Item",
        "prefixes": "Item",
    }
    for key, osw_obj_list in entities_dict.items():
        ns = ns_map.get(key, "")
        for entity in osw_obj_list:
            iri = entity.get_iri()
            entity_map[iri] = entity
            # Also index with namespace prefix for __iris__ lookups
            if ns and not iri.startswith(ns + ":"):
                entity_map[f"{ns}:{iri}"] = entity

    quantity_property_entities = {}
    for osw_characteristic in entities_dict.get("fundamental_characteristics", []):
        quantity_iri = osw_characteristic.__iris__.get("quantity")
        osw_quantity = entity_map.get(quantity_iri)
        if osw_quantity is None:
            continue
        unit_iris = sorted(osw_quantity.__iris__.get("units", []))
        units = [entity_map[u] for u in unit_iris if u in entity_map]
        sub_units = []
        for u in units:
            if hasattr(u, "prefix_units") and u.prefix_units is not None:
                sub_units.extend(u.prefix_units)
            if hasattr(u, "composed_units") and u.composed_units is not None:
                sub_units.extend(u.composed_units)
        units.extend(sub_units)

        main_unit = None
        other_units = []
        for unit in units:
            cf = getattr(unit, "conversion_factor_from_si", None)
            if cf is not None and float(cf) == 1.0 and main_unit is None:
                main_unit = unit
            else:
                other_units.append(unit)
        if main_unit is None and len(other_units) == 1:
            warning(
                "Only one unit with conversion_factor != 1.0 for: "
                + osw_characteristic.name + ". Using as main unit."
            )
            main_unit = other_units[0]
            other_units = []
        if main_unit is None and units:
            warning("No main unit found for: " + osw_characteristic.name)
            main_unit = units[0]
            other_units = units[1:]
        if main_unit is None:
            continue

        def _get_osw_id(entity):
            osw_id = getattr(entity, "osw_id", None)
            uuid_ = entity.get_uuid()
            from_uuid = None if uuid_ is None else f"OSW{str(uuid_).replace('-', '')}"
            return osw_id or from_uuid

        additional_units = []
        main_sub_units = []
        if hasattr(main_unit, "prefix_units") and main_unit.prefix_units is not None:
            main_sub_units.extend(main_unit.prefix_units)
        if hasattr(main_unit, "composed_units") and main_unit.composed_units is not None:
            main_sub_units.extend(main_unit.composed_units)
        for pu in main_sub_units:
            cf = getattr(pu, "conversion_factor_from_si", None)
            if cf is None:
                warning("No conversion factor for unit: " + str(pu.main_symbol))
                continue
            if float(cf) == 0:
                warning(f"Conversion factor 0 for: {pu.main_symbol}")
                continue
            main_cf = float(main_unit.conversion_factor_from_si) if main_unit.conversion_factor_from_si else 0
            # conversion_factor_to_main_unit * unit_value = main_unit_value
            # e.g., 100 * 1 cm = 1 m → factor = main_cf / cf = 1.0 / 0.01 = 100
            additional_units.append(model.Unit(
                uuid=_make_uuid("smwunit:" + str(pu.uuid)),
                name=pu.main_symbol,
                main_symbol=pu.main_symbol,
                conversion_factor_to_main_unit=(
                    main_cf / float(cf) if float(cf) != 0 else None
                ),
            ))

        for unit in other_units:
            if not hasattr(unit, "main_symbol"):
                continue
            cf = getattr(unit, "conversion_factor_from_si", None)
            if cf is None or float(cf) == 0:
                continue
            main_cf = float(main_unit.conversion_factor_from_si) if main_unit.conversion_factor_from_si else 0
            additional_units.append(model.Unit(
                uuid=_make_uuid("smwunit:" + str(getattr(unit, "uuid", unit.main_symbol))),
                name=unit.main_symbol,
                main_symbol=unit.main_symbol,
                conversion_factor_to_main_unit=(
                    main_cf / float(cf) if float(cf) != 0 else None
                ),
            ))

        # Deduplicate by symbol and sort by conversion factor
        seen = {main_unit.main_symbol}
        deduped = []
        for u in additional_units:
            if u.main_symbol not in seen:
                seen.add(u.main_symbol)
                deduped.append(u)
        additional_units = sorted(
            deduped,
            key=lambda u: (
                float(u.conversion_factor_to_main_unit) if u.conversion_factor_to_main_unit else float("inf"),
                u.main_symbol,
            ),
        )

        prop_name = f"Has{osw_characteristic.name}Value"
        title = f"Property:{prop_name}"
        prop = model.MainQuantityProperty(
            uuid=_make_uuid("property:" + osw_characteristic.name),
            meta=model.Meta(
                uuid=_make_uuid("meta:" + title),
                wiki_page=model.WikiPage(title=prop_name, namespace="Property"),
            ),
            name=prop_name,
            label=osw_characteristic.label,
            description=osw_characteristic.description,
            main_unit=model.Unit(
                uuid=_make_uuid("smwunit:" + str(getattr(main_unit, "uuid", main_unit.main_symbol))),
                name=main_unit.main_symbol,
                main_symbol=main_unit.main_symbol,
                conversion_factor_to_main_unit=1.0,
            ),
            additional_units=additional_units if additional_units else None,
        )
        quantity_property_entities[title] = prop

    # Create SubQuantityProperty for non-fundamental characteristics
    for osw_characteristic in entities_dict.get("characteristics", []):
        prop_name = f"Has{osw_characteristic.name}Value"
        title = f"Property:{prop_name}"

        subclass_iris = osw_characteristic.__iris__.get("subclass_of", [])
        broader_cat = subclass_iris[0] if subclass_iris else None
        base_characteristic = entity_map.get(broader_cat)
        base_property_title = None
        if base_characteristic:
            base_property_title = f"Property:Has{base_characteristic.name}Value"

        if base_property_title is None:
            continue

        prop = model.SubQuantityProperty(
            uuid=_make_uuid("property:" + osw_characteristic.name),
            meta=model.Meta(
                uuid=_make_uuid("meta:" + title),
                wiki_page=model.WikiPage(title=prop_name, namespace="Property"),
            ),
            name=prop_name,
            label=osw_characteristic.label,
            description=osw_characteristic.description,
            subproperty_of=base_property_title,
            base_property=base_property_title,
        )
        quantity_property_entities[title] = prop

    return quantity_property_entities


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
            "Category:OSWffe74f291d354037b318c422591c5023",  # Characteristic Type
            "Category:OSW4082937906634af992cf9a1b18d772cf",  # Quantity Value
            "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7",  # Fundamental Quantity Value Type
            "Category:OSWac07a46c2cf14f3daec503136861f5ab",  # Quantity Value Type
            "Category:OSW1b15ddcf042c4599bd9d431cbfdf3430",  # Main Quantity Property
            "Category:OSW69f251a900944602a08d1cca830249b5",  # Sub Quantity Property
        ],
        mode="append",
    )
)

cache = False
cache_file = Path(__file__).parent / "list_of_osw_obj_dict.pickle"

if cache and cache_file.exists():
    with open(cache_file, "rb") as f:
        entities_dict = pickle.load(f)
else:
    # Load enriched QUDT data
    data = load_enriched_qudt(ENRICHED_QUDT_PATH)
    print(f"Loaded enriched QUDT: {len(data['graph'])} items")

    # Create entities
    prefix_entities = get_unit_prefix_entities(data)
    print(f"Created {len(prefix_entities)} UnitPrefix entities")

    non_composed, composed, unit_id_to_osw_id = get_quantity_unit_entities(data)
    print(f"Created {len(non_composed)} QuantityUnit + {len(composed)} ComposedUnit entities")

    # Build unit entities map (OSW ID -> entity) for characteristic creation
    unit_entities_map = {}
    for u in non_composed:
        osw_id = f"Item:OSW{str(u.uuid).replace('-', '')}"
        unit_entities_map[osw_id] = u
    for u in composed:
        osw_id = f"Item:OSW{str(u.uuid).replace('-', '')}"
        unit_entities_map[osw_id] = u

    qk_list, fund_chars, chars = get_quantitykind_and_characteristics(
        data, unit_id_to_osw_id, unit_entities_map
    )
    print(
        f"Created {len(qk_list)} QuantityKind, "
        f"{len(fund_chars)} fundamental, {len(chars)} non-fundamental characteristics"
    )

    entities_dict = {
        "prefixes": prefix_entities,
        "quantity_units": non_composed,
        "composed_prefix_quantity_units": composed,
        "quantity_kinds": qk_list,
        "fundamental_characteristics": fund_chars,
        "characteristics": chars,
    }

    with open(cache_file, "wb") as f:
        pickle.dump(entities_dict, f)

quantity_property_entities = create_smw_quantity_properties(
    entities_dict=entities_dict
)
p_entities = list(quantity_property_entities.values())

keys_to_keep = [
    "fundamental_characteristics",
    "characteristics",
]
entities_dict = {key: entities_dict[key] for key in keys_to_keep}
entities_dict["properties"] = p_entities

pages: Dict[str, WtPage] = {}

for key, osw_obj_list in entities_dict.items():
    namespace = None
    meta_category_title = None
    if key == "fundamental_characteristics":
        namespace = "Category"
        meta_category_title = "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7"
    if key == "characteristics":
        namespace = "Category"
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
    "Category:OSWac07a46c2cf14f3daec503136861f5ab",  # "Quantity Value Type",
    "Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7",  # "Fundamental Quantity Value Type",
]
page_titles.extend(sorted(pages.keys()))

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

# Provide information on the page package to be created
package_meta_data = WorldMeta(
    name="OSW Quantitive Characteristics",
    repo="world.opensemantic.characteristics.quantitative",
    id="world.opensemantic.characteristics.quantitative",
    subdir="base",
    branch="main",
    description=("Contains measureable qualitities based on (physical) quantities"),
    version="0.3.0",
    requiredPackages=[
        "world.opensemantic.quantities",
    ],
    author=["Andreas Räder", "Matthias Albert Popp", "Simon Stier", "Lukas Gold"],
    page_titles=page_titles,
)
package_creation_config = WorldCreat(
    working_dir=Path(__file__).parents[1] / "packages" / package_meta_data.repo,
    offline_pages=pages,
    generate_python_code=False,  # handled by tools/osw-python-package-generator
    generate_package_documentation_page=True,
    python_code_working_dir=(
        Path(__file__).parents[1]
        / "python_packages"
        / (package_meta_data.id.replace("world.", "") + "-python")
        / "src"
    ).joinpath(
        *[part for part in package_meta_data.id.replace("world.", "").split(".")]
    ),
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
