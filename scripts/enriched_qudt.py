"""Shared module for reading enriched QUDT JSON-LD and creating OSW entities.

Used by:
- world.opensemantic.characteristics.quantitative.py
- world.opensemantic.quantities.py
"""

import json
import uuid as uuid_module
from pathlib import Path

from osw.utils.strings import pascal_case
from osw.utils.wiki import get_full_title


ENRICHED_QUDT_PATH = (
    Path(__file__).parent.parent
    / "tools"
    / "qudt-parsing"
    / "data"
    / "qudt_dump.enriched.json"
)

PATCHES_PATH = (
    Path(__file__).parent.parent
    / "tools"
    / "qudt-parsing"
    / "data"
    / "patches.json"
)

# Symbol overrides for enum name generation. Extended by patches.json at load time.
SYMBOL_OVERRIDES = {"一": "unitless", "#": "dimensionless", "%": "percent", "pH": "pH_value"}


def _make_uuid(uri: str) -> str:
    return str(uuid_module.uuid5(namespace=uuid_module.NAMESPACE_URL, name=uri))


def _make_osw_id(uri: str, namespace: str = "Item") -> str:
    return f"{namespace}:OSW{_make_uuid(uri).replace('-', '')}"


def _resolve_curie(curie: str, context: dict) -> str:
    if ":" not in curie or curie.startswith("http"):
        return curie
    prefix, suffix = curie.split(":", 1)
    base = context.get(prefix)
    if base:
        return base + suffix
    return curie


def _get_values(inp, key: str) -> list:
    if isinstance(inp, dict):
        if key in inp:
            return [inp[key]]
        return []
    elif isinstance(inp, list):
        return [item[key] for item in inp if isinstance(item, dict) and key in item]
    return []


def _get_labels(item: dict) -> list:
    """Extract labels from rdfs:label, returns list of model.Label."""
    import opensemantic.core as _core
    import opensemantic.quantities as _quantities
    import opensemantic.characteristics.quantitative as _char_quant
    import types
    model = types.SimpleNamespace(
        **{k: v for m in [_core, _quantities, _char_quant]
           for k, v in vars(m).items() if not k.startswith("_")}
    )

    raw = item.get("rdfs:label")
    if raw is None:
        return []
    if isinstance(raw, str):
        return [model.Label(text=raw, lang="en")]
    if isinstance(raw, dict):
        lang = raw.get("@language", "en")
        text = raw.get("@value", raw.get("text", ""))
        if lang in ("en", "de", ""):
            return [model.Label(text=text, lang=lang if lang else "en")]
        return []
    if isinstance(raw, list):
        labels = []
        for entry in raw:
            if isinstance(entry, str):
                labels.append(model.Label(text=entry, lang="en"))
            elif isinstance(entry, dict):
                lang = entry.get("@language", "en")
                text = entry.get("@value", entry.get("text", ""))
                if lang in ("en", "de", "en-US", ""):
                    actual_lang = "en" if lang in ("en-US", "") else lang
                    labels.append(model.Label(text=text, lang=actual_lang))
        return labels
    return []


def _get_descriptions(item: dict) -> list:
    import opensemantic.core as _core
    import opensemantic.quantities as _quantities
    import opensemantic.characteristics.quantitative as _char_quant
    import types
    model = types.SimpleNamespace(
        **{k: v for m in [_core, _quantities, _char_quant]
           for k, v in vars(m).items() if not k.startswith("_")}
    )

    def _clean(text: str) -> str:
        t = text.strip()
        if t.startswith("AI-generated: "):
            t = t[len("AI-generated: "):]
        return t

    for attr in ("qudt:plainTextDescription", "dcterms:description"):
        raw = item.get(attr)
        if raw is None:
            continue
        if isinstance(raw, str):
            if raw.strip():
                return [model.Description(text=_clean(raw), lang="en")]
        elif isinstance(raw, dict):
            text = raw.get("@value", "").strip()
            if text:
                return [model.Description(text=_clean(text), lang="en")]
        elif isinstance(raw, list):
            for entry in raw:
                text = entry.get("@value", "") if isinstance(entry, dict) else str(entry)
                if text.strip():
                    return [model.Description(text=_clean(text), lang="en")]
    return []


def _is_si_applicable(unit_item: dict) -> bool:
    systems = unit_item.get("qudt:applicableSystem", [])
    if isinstance(systems, dict):
        systems = [systems]
    return any(s.get("@id") == "sou:SI" for s in systems if isinstance(s, dict))


def _sort_labels(labels):
    return sorted(labels, key=lambda x: x.lang != "en")


KNOWN_PREFIXES = {
    "Atto", "Centi", "Deca", "Deci", "Deka", "Exa", "Exbi", "Femto",
    "Gibi", "Giga", "Hecto", "Kibi", "Kilo", "Mebi", "Mega", "Micro",
    "Milli", "Nano", "Pebi", "Peta", "Pico", "Quecto", "Quetta", "Ronna",
    "Ronto", "Tebi", "Tera", "Yobi", "Yocto", "Yotta", "Zebi", "Zepto",
    "Zetta",
}


def _prefix_in(name: str) -> bool:
    return any(name.startswith(p) for p in KNOWN_PREFIXES)


def _sort_entity_arrays(entity):
    """Sort list-of-string fields on an entity for deterministic output.
    Uses __dict__ to avoid triggering oo-ld's object graph resolver."""
    d = entity.__dict__
    for field_name in ("exact_ontology_match", "close_ontology_match", "units"):
        val = d.get(field_name)
        if isinstance(val, list) and all(isinstance(v, str) for v in val):
            val.sort()
    # Sort sub-entity lists by osw_id or uuid
    for field_name in ("prefix_units", "composed_units"):
        val = d.get(field_name)
        if isinstance(val, list):
            val.sort(key=lambda x: getattr(x, "osw_id", "") or str(getattr(x, "uuid", "")) or "")


def _get_unit_enum_name(symbol: str, ucum_codes: list) -> str:
    """Convert a unit symbol to a valid Python identifier using pint/ucumvert.
    Returns None if conversion fails."""
    if not hasattr(_get_unit_enum_name, "_ureg"):
        from pint import UnitRegistry
        from ucumvert import PintUcumRegistry
        _get_unit_enum_name._ureg = UnitRegistry()
        _get_unit_enum_name._ucum_ureg = PintUcumRegistry()
    ureg = _get_unit_enum_name._ureg
    ucum_ureg = _get_unit_enum_name._ucum_ureg

    # Handle special symbols (can be extended by patches.json symbol_overrides)
    if symbol in SYMBOL_OVERRIDES:
        return SYMBOL_OVERRIDES[symbol]

    pQ = None
    try:
        sym = symbol
        if sym.startswith("/"):
            sym = "1" + sym
        sym = sym.replace("\u00b0C", "delta_degC").replace("\u00b0F", "delta_degF")
        sym = sym.replace("2", "\u00b2").replace("3", "\u00b3").replace("4", "\u2074")
        sym = sym.replace("#", "")
        pQ = ureg(sym)
    except Exception:
        pass

    if pQ is None:
        for code in ucum_codes or []:
            try:
                pQ = ucum_ureg.from_ucum(code)
                break
            except Exception:
                continue

    if pQ is None:
        return None

    import re

    value = f"{pQ:9fLx}"
    # Handle pint's \tothe{N} pattern before extracting the unit block
    EXPONENT_WORDS = {
        "2": "squared", "3": "cubed", "4": "to_the_fourth",
        "5": "to_the_fifth", "6": "to_the_sixth",
    }
    value = re.sub(
        r"\\tothe\{(\d+)\}",
        lambda m: "\\" + EXPONENT_WORDS.get(m.group(1), "to_the_" + m.group(1)),
        value,
    )
    # Now safe to extract the last {unit} block
    siunix_symbol = value.split("{")[-1].replace("}", "")
    siunix_symbol = siunix_symbol.replace("delta_degree_Fahrenheit", "Fahrenheit")
    siunix_symbol = siunix_symbol.replace("delta_degree_Celsius", "Celsius")
    siunix_symbol = siunix_symbol.replace("\\", "_").strip("_")
    if not siunix_symbol:
        return None
    # Check if pint changed the scale (magnitude != 1.0) — if so, the symbol
    # no longer matches the original unit and we should fall back
    magnitude = float(value.split("{")[1].split("}")[0])
    if abs(magnitude - 1.0) > 1e-9:
        return _sanitize_identifier(symbol)
    # Replace exponent digits with words (digits in pint output are exponents)
    EXPONENT_WORDS = {
        "2": "squared", "3": "cubed", "4": "to_the_fourth",
        "5": "to_the_fifth", "6": "to_the_sixth",
    }
    siunix_symbol = re.sub(
        r"(\d+)",
        lambda m: EXPONENT_WORDS.get(m.group(1), "to_the_" + m.group(1)),
        siunix_symbol,
    )
    # Ensure valid Python identifier
    if not siunix_symbol.isidentifier():
        siunix_symbol = _sanitize_identifier(siunix_symbol)
    return siunix_symbol if siunix_symbol else None


def _sanitize_identifier(name: str) -> str:
    """Sanitize a unit symbol string into a valid, readable Python identifier.
    Digits are treated as exponents (from unit symbols), not literal numbers."""
    import re

    EXPONENT_WORDS = {
        "2": "squared", "3": "cubed", "4": "to_the_fourth",
        "5": "to_the_fifth", "6": "to_the_sixth",
        "7": "to_the_seventh", "8": "to_the_eighth", "9": "to_the_ninth",
    }
    # Order matters — longer replacements first to avoid partial matches
    SYMBOL_REPLACEMENTS = [
        ("лв.", "lev"),
        ("лв", "lev"),
        ("stat℧", "statmho"),
        ("℧", "mho"),
        ("μ", "micro_"),
        ("°C", "degree_celsius"),
        ("°F", "degree_fahrenheit"),
        ("°", "degree_"),
        ("€", "euro"),
        ("£", "pound"),
        ("CHF", "chf"),
        ("Ft", "forint"),
        ("Kč", "koruna"),
        ("kr", "krone"),
        ("zł", "zloty"),
        ("²", "_squared"),
        ("³", "_cubed"),
        ("⁴", "_to_the_fourth"),
        ("/", "_per_"),
        ("·", "_"),
        ("{", "_"),
        ("}", ""),
        ("(", ""),
        (")", ""),
        (".", "_"),
    ]

    result = name
    for old, new in SYMBOL_REPLACEMENTS:
        result = result.replace(old, new)

    # Replace remaining non-ASCII characters
    result = re.sub(r"[^a-zA-Z0-9_]", "_", result)

    # Collapse multiple underscores, strip leading/trailing
    result = re.sub(r"_+", "_", result).strip("_")

    # Replace standalone digits with exponent words
    result = re.sub(
        r"(\d+)",
        lambda m: EXPONENT_WORDS.get(m.group(1), "to_the_" + m.group(1)),
        result,
    )
    result = re.sub(r"_+", "_", result).strip("_")

    return result if result else "unknown"


def _apply_patches(graph: list, id_dict: dict, patches_path: Path):
    """Apply QUDT data corrections from patches.json."""
    if not patches_path.exists():
        return
    with open(patches_path, encoding="utf-8") as f:
        patches = json.load(f)

    # Remove incorrect scalingOf relationships
    for unit_id, target in patches.get("remove_scaling_of", {}).items():
        if unit_id.startswith("_"):
            continue
        item = id_dict.get(unit_id)
        if item and "qudt:scalingOf" in item:
            so = item["qudt:scalingOf"]
            if isinstance(so, dict) and so.get("@id") == target:
                del item["qudt:scalingOf"]
            elif isinstance(so, list):
                item["qudt:scalingOf"] = [
                    s for s in so
                    if not (isinstance(s, dict) and s.get("@id") == target)
                ]

    # Remove wrong applicableUnit entries
    for qk_id, units_to_remove in patches.get("remove_applicable_units", {}).items():
        if qk_id.startswith("_"):
            continue
        qk = id_dict.get(qk_id)
        if qk and "qudt:applicableUnit" in qk:
            aus = qk["qudt:applicableUnit"]
            qk["qudt:applicableUnit"] = [
                au for au in aus
                if not (isinstance(au, dict) and au.get("@id") in units_to_remove)
            ]

    # Fix description language tags
    for qk_id, correct_lang in patches.get("fix_description_lang", {}).items():
        if qk_id.startswith("_"):
            continue
        qk = id_dict.get(qk_id)
        if qk:
            desc = qk.get("dcterms:description")
            if isinstance(desc, dict) and desc.get("@language") == "en":
                desc["@language"] = correct_lang
            elif isinstance(desc, list):
                for d in desc:
                    if isinstance(d, dict) and d.get("@language") == "en":
                        d["@language"] = correct_lang

    # Fix labels
    for qk_id, fixes in patches.get("fix_labels", {}).items():
        if qk_id.startswith("_"):
            continue
        qk = id_dict.get(qk_id)
        if qk and "label_en" in fixes:
            label = qk.get("rdfs:label")
            if isinstance(label, dict) and label.get("@language") == "en":
                label["@value"] = fixes["label_en"]
            elif isinstance(label, list):
                for lbl in label:
                    if isinstance(lbl, dict) and lbl.get("@language") == "en":
                        lbl["@value"] = fixes["label_en"]

    # Set/replace descriptions
    for qk_id, lang_texts in patches.get("set_descriptions", {}).items():
        if qk_id.startswith("_"):
            continue
        qk = id_dict.get(qk_id)
        if qk:
            for lang, text in lang_texts.items():
                desc = qk.get("dcterms:description")
                if isinstance(desc, dict):
                    if desc.get("@language") == lang:
                        desc["@value"] = text
                    else:
                        qk["dcterms:description"] = [desc, {"@language": lang, "@value": text}]
                elif isinstance(desc, list):
                    found = False
                    for d in desc:
                        if isinstance(d, dict) and d.get("@language") == lang:
                            d["@value"] = text
                            found = True
                    if not found:
                        desc.append({"@language": lang, "@value": text})
                else:
                    qk["dcterms:description"] = {"@language": lang, "@value": text}

    # Fix/add skos:broader relationships
    for qk_id, broader_id in patches.get("fix_broader", {}).items():
        if qk_id.startswith("_"):
            continue
        qk = id_dict.get(qk_id)
        if qk:
            qk["skos:broader"] = {"@id": broader_id}

    # Load symbol overrides from patches into SYMBOL_OVERRIDES
    for sym, override in patches.get("symbol_overrides", {}).items():
        if sym.startswith("_"):
            continue
        SYMBOL_OVERRIDES[sym] = override


def load_enriched_qudt(path: Path, patches_path: Path = PATCHES_PATH) -> dict:
    """Load enriched QUDT JSON-LD, apply patches, and build indices."""
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    context = raw.get("@context", {})
    graph = raw.get("@graph", [])

    id_dict = {}
    type_items = {}
    for item in graph:
        item_id = item.get("@id", "")
        if item_id:
            id_dict[item_id] = item
        types = item.get("@type", [])
        if isinstance(types, str):
            types = [types]
        for t in types:
            type_items.setdefault(t, []).append(item)

    _apply_patches(graph, id_dict, patches_path)

    return {
        "context": context,
        "graph": graph,
        "id_dict": id_dict,
        "type_items": type_items,
    }


def get_unit_prefix_entities(data: dict):
    import opensemantic.core as _core
    import opensemantic.quantities as _quantities
    import opensemantic.characteristics.quantitative as _char_quant
    import types
    model = types.SimpleNamespace(
        **{k: v for m in [_core, _quantities, _char_quant]
           for k, v in vars(m).items() if not k.startswith("_")}
    )

    prefixes = data["type_items"].get("qudt:Prefix", [])
    context = data["context"]
    entities = []
    for item in prefixes:
        item_id = item.get("@id", "")
        full_uri = _resolve_curie(item_id, context)
        labels = _sort_labels(_get_labels(item))
        descriptions = _get_descriptions(item)
        name = labels[0].text.lower() if labels else item_id.split(":")[-1].lower()
        factor = None
        mult = item.get("qudt:prefixMultiplier")
        if isinstance(mult, dict):
            factor = mult.get("@value")
        elif mult is not None:
            factor = mult
        exact_matches = [full_uri]
        for same_as in _get_values(item.get("owl:sameAs", []), "@id"):
            exact_matches.append(_resolve_curie(same_as, context))

        # Use SI Digital Framework URI for UUID if available (backward compat)
        uuid_uri = full_uri
        si_match = item.get("qudt:siExactMatch")
        if isinstance(si_match, dict) and "@id" in si_match:
            resolved_si = _resolve_curie(si_match["@id"], context)
            if "si-digital-framework.org" in resolved_si:
                uuid_uri = resolved_si
                exact_matches.append(resolved_si)
        elif isinstance(si_match, list):
            for m in si_match:
                if isinstance(m, dict) and "@id" in m:
                    resolved_si = _resolve_curie(m["@id"], context)
                    if "si-digital-framework.org" in resolved_si:
                        uuid_uri = resolved_si
                        exact_matches.append(resolved_si)
                        break

        # Lowercase labels for prefixes (SI convention)
        for lbl in labels:
            lbl.text = lbl.text.lower()
        entities.append(model.UnitPrefix(
            uuid=_make_uuid(uuid_uri),
            name=name,
            label=labels,
            description=descriptions,
            symbol=item.get("qudt:symbol", ""),
            factor=factor,
            exact_ontology_match=sorted(set(exact_matches)),
        ))
        _sort_entity_arrays(entities[-1])
    return entities


def get_quantity_unit_entities(data: dict):
    """Create QuantityUnit and ComposedQuantityUnitWithUnitPrefix entities.

    Returns (non_composed_units, composed_units, unit_id_to_osw_id).
    """
    import opensemantic.core as _core
    import opensemantic.quantities as _quantities
    import opensemantic.characteristics.quantitative as _char_quant
    import types
    model = types.SimpleNamespace(
        **{k: v for m in [_core, _quantities, _char_quant]
           for k, v in vars(m).items() if not k.startswith("_")}
    )

    context = data["context"]
    id_dict = data["id_dict"]
    units = data["type_items"].get("qudt:Unit", [])

    # Pre-compute: which non-SI units have at least one SI prefixed variant?
    non_si_with_si_variant = set()
    for item in units:
        if _is_si_applicable(item):
            continue
        item_id = item.get("@id", "")
        scaled_by = [sb.get("@id", "") for sb in item.get("custom:scaledBy", []) if isinstance(sb, dict)]
        for sb_id in scaled_by:
            sb_item = id_dict.get(sb_id)
            if sb_item and _is_si_applicable(sb_item):
                non_si_with_si_variant.add(item_id)
                break

    non_prefixed_non_composed = []
    non_prefixed_composed = []
    for item in units:
        if not _is_si_applicable(item) and item.get("@id", "") not in non_si_with_si_variant:
            continue
        item_id = item.get("@id", "")
        local_name = item_id.split(":")[-1] if ":" in item_id else item_id
        has_factor_units = "qudt:hasFactorUnit" in item
        has_prefix = "qudt:prefix" in item
        is_scaling_of = "qudt:scalingOf" in item
        is_prefixed = has_prefix or (
            is_scaling_of and not has_factor_units and _prefix_in(local_name)
        )
        # Also skip composed units that are scalings of another composed unit
        # (e.g. MilliM2 is scalingOf M2 — it becomes a subobject of M2)
        # Only if the base unit also has factor units AND lists this unit in scaledBy
        is_prefixed_composed = False
        if has_factor_units and is_scaling_of and _prefix_in(local_name):
            scaling = item.get("qudt:scalingOf", [])
            if isinstance(scaling, dict):
                scaling = [scaling]
            for s in scaling:
                base_id = s.get("@id", "") if isinstance(s, dict) else s
                base_item = id_dict.get(base_id)
                if base_item and "qudt:hasFactorUnit" in base_item:
                    scaled_by = [sb.get("@id", "") for sb in base_item.get("custom:scaledBy", []) if isinstance(sb, dict)]
                    if item_id in scaled_by:
                        is_prefixed_composed = True
                        break
        if is_prefixed or is_prefixed_composed:
            continue
        if has_factor_units:
            non_prefixed_composed.append(item)
        else:
            non_prefixed_non_composed.append(item)

    unit_id_to_osw_id = {}
    non_composed_entities = []
    composed_entities = []

    def _make_factor_unit_osw_id(fu_id):
        fu_full_uri = _resolve_curie(fu_id, context)
        fu_local = fu_id.split(":")[-1] if ":" in fu_id else fu_id
        if _prefix_in(fu_local):
            fu_item = id_dict.get(fu_id)
            base_id = None
            if fu_item and "qudt:scalingOf" in fu_item:
                scaling = fu_item["qudt:scalingOf"]
                if isinstance(scaling, list):
                    scaling = scaling[0] if scaling else {}
                base_id = scaling.get("@id", fu_id) if isinstance(scaling, dict) else fu_id
            if base_id:
                base_full = _resolve_curie(base_id, context)
                return f"Item:OSW{_make_uuid(base_full).replace('-', '')}#OSW{_make_uuid(fu_full_uri).replace('-', '')}"
        return f"Item:OSW{_make_uuid(fu_full_uri).replace('-', '')}"

    def _extract_factor_units(item_dict):
        result = []
        item_id = item_dict.get("@id", "")
        for fu_dict in item_dict.get("qudt:hasFactorUnit", []):
            fu_id = fu_dict.get("qudt:hasUnit", {}).get("@id", "")
            fu_exp = fu_dict.get("qudt:exponent", {})
            fu_exp_val = fu_exp.get("@value", 1) if isinstance(fu_exp, dict) else fu_exp
            fu_uuid = _make_uuid(f"{item_id}#factorUnit#{fu_id}#{fu_exp_val}")
            result.append({
                "uuid": fu_uuid,
                "unit": _make_factor_unit_osw_id(fu_id),
                "exponent": fu_exp_val,
            })
        return result

    def _get_conv_factor(item_dict):
        conv = item_dict.get("qudt:conversionMultiplier", {})
        return conv.get("@value") if isinstance(conv, dict) else conv

    def _get_ucum(item_dict):
        codes = _get_values(item_dict.get("qudt:ucumCode", []), "@value")
        if not codes and isinstance(item_dict.get("qudt:ucumCode"), str):
            codes = [item_dict["qudt:ucumCode"]]
        return codes

    # Process non-composed units
    for npu in non_prefixed_non_composed:
        npu_id = npu.get("@id", "")
        full_uri = _resolve_curie(npu_id, context)
        npu_uuid = _make_uuid(full_uri)
        npu_osw_id = f"Item:OSW{npu_uuid.replace('-', '')}"
        unit_id_to_osw_id[npu_id] = npu_osw_id

        labels = _sort_labels(_get_labels(npu))
        descriptions = _get_descriptions(npu)

        prefix_unit_list = []
        for pu_ref in _get_values(npu.get("custom:scaledBy", []), "@id"):
            pu_item = id_dict.get(pu_ref)
            if pu_item is None:
                continue
            pu_full_uri = _resolve_curie(pu_ref, context)
            pu_uuid = _make_uuid(pu_full_uri)
            pu_osw_id = f"Item:OSW{npu_uuid.replace('-', '')}#OSW{pu_uuid.replace('-', '')}"
            unit_id_to_osw_id[pu_ref] = pu_osw_id

            prefix_ref = pu_item.get("qudt:prefix", {})
            prefix_id = prefix_ref.get("@id", "") if isinstance(prefix_ref, dict) else ""
            prefix_full_uri = _resolve_curie(prefix_id, context) if prefix_id else ""
            prefix_osw_id = f"Item:OSW{_make_uuid(prefix_full_uri).replace('-', '')}" if prefix_full_uri else ""
            prefix_symbol = ""
            prefix_item = id_dict.get(prefix_id)
            if prefix_item:
                prefix_symbol = prefix_item.get("qudt:symbol", "")

            pu_conv = _get_conv_factor(pu_item)
            npu_conv = _get_conv_factor(npu)
            conv_to_main = None
            if pu_conv is not None and npu_conv is not None:
                try:
                    conv_to_main = float(pu_conv) / float(npu_conv) if float(npu_conv) != 0 else None
                except (ValueError, TypeError):
                    pass

            prefix_unit_list.append(model.PrefixUnit(
                uuid=pu_uuid,
                osw_id=pu_osw_id,
                main_symbol=pu_item.get("qudt:symbol", ""),
                conversion_factor_to_main_unit=conv_to_main if conv_to_main is not None else 1.0,
                conversion_factor_from_si=pu_conv,
                prefix=prefix_osw_id,
                prefix_symbol=prefix_symbol,
                ucum_codes=_get_ucum(pu_item),
            ))

        non_composed_entities.append(model.QuantityUnit(
            uuid=npu_uuid,
            name=pascal_case(labels[0].text) if labels else (npu_id.split(":")[-1] if ":" in npu_id else npu_id),
            label=labels,
            description=descriptions,
            main_symbol=npu.get("qudt:symbol", npu_id.split(":")[-1]),
            conversion_factor_from_si=_get_conv_factor(npu),
            ucum_codes=_get_ucum(npu),
            prefix_units=prefix_unit_list if prefix_unit_list else None,
            exact_ontology_match=[full_uri],
        ))

    # Process composed units
    for npcu in non_prefixed_composed:
        npcu_id = npcu.get("@id", "")
        full_uri = _resolve_curie(npcu_id, context)
        npcu_uuid = _make_uuid(full_uri)
        npcu_osw_id = f"Item:OSW{npcu_uuid.replace('-', '')}"
        unit_id_to_osw_id[npcu_id] = npcu_osw_id

        labels = _sort_labels(_get_labels(npcu))
        descriptions = _get_descriptions(npcu)

        composed_unit_list = []
        for pcu_ref in _get_values(npcu.get("custom:scaledBy", []), "@id"):
            pcu_item = id_dict.get(pcu_ref)
            if pcu_item is None:
                continue
            pcu_full_uri = _resolve_curie(pcu_ref, context)
            pcu_uuid = _make_uuid(pcu_full_uri)
            pcu_osw_id = f"Item:OSW{npcu_uuid.replace('-', '')}#OSW{pcu_uuid.replace('-', '')}"
            unit_id_to_osw_id[pcu_ref] = pcu_osw_id

            pcu_conv = _get_conv_factor(pcu_item)
            npcu_conv = _get_conv_factor(npcu)
            pcu_conv_to_main = None
            if pcu_conv is not None and npcu_conv is not None:
                try:
                    pcu_conv_to_main = float(pcu_conv) / float(npcu_conv) if float(npcu_conv) != 0 else None
                except (ValueError, TypeError):
                    pass

            sub_cls = getattr(model, "ComposedUnitElement", model.ComposedUnit)
            sub_kwargs = dict(
                uuid=pcu_uuid,
                osw_id=pcu_osw_id,
                main_symbol=pcu_item.get("qudt:symbol", ""),
                conversion_factor_from_si=pcu_conv,
                ucum_codes=_get_ucum(pcu_item),
                factor_units=_extract_factor_units(pcu_item) or _extract_factor_units(npcu) or [],
            )
            if "conversion_factor_to_main_unit" in sub_cls.__fields__:
                sub_kwargs["conversion_factor_to_main_unit"] = pcu_conv_to_main if pcu_conv_to_main is not None else 1.0
            composed_unit_list.append(sub_cls(**sub_kwargs))

        composed_entities.append(model.ComposedUnit(
            uuid=npcu_uuid,
            osw_id=f"OSW{npcu_uuid.replace('-', '')}",
            name=pascal_case(labels[0].text) if labels else (npcu_id.split(":")[-1] if ":" in npcu_id else npcu_id),
            label=labels,
            description=descriptions,
            main_symbol=npcu.get("qudt:symbol", npcu_id.split(":")[-1]),
            conversion_factor_from_si=_get_conv_factor(npcu),
            conversion_factor_to_main_unit=1.0,
            ucum_codes=_get_ucum(npcu),
            factor_units=_extract_factor_units(npcu) or None,
            composed_units=composed_unit_list if composed_unit_list else None,
            exact_ontology_match=[full_uri],
        ))

    for e in non_composed_entities:
        _sort_entity_arrays(e)
    for e in composed_entities:
        _sort_entity_arrays(e)
    return non_composed_entities, composed_entities, unit_id_to_osw_id


def _expand_applicable_units(applicable_units: list, id_dict: dict) -> list:
    """Expand applicable units: add base units via scalingOf, add all scaledBy variants."""
    expanded = set(applicable_units)
    base_units_found = set()
    for au_id in applicable_units:
        au_item = id_dict.get(au_id)
        if au_item and "qudt:scalingOf" in au_item:
            scaling = au_item["qudt:scalingOf"]
            if isinstance(scaling, list):
                for s in scaling:
                    base_id = s.get("@id", "") if isinstance(s, dict) else s
                    if base_id:
                        expanded.add(base_id)
                        base_units_found.add(base_id)
            elif isinstance(scaling, dict):
                base_id = scaling.get("@id", "")
                if base_id:
                    expanded.add(base_id)
                    base_units_found.add(base_id)
    for au_id in applicable_units:
        au_item = id_dict.get(au_id)
        if au_item and "custom:scaledBy" in au_item:
            base_units_found.add(au_id)
    for base_id in base_units_found:
        base_item = id_dict.get(base_id)
        if base_item and "custom:scaledBy" in base_item:
            for scaled_ref in _get_values(base_item.get("custom:scaledBy", []), "@id"):
                expanded.add(scaled_ref)
    return list(expanded)


def get_quantitykind_and_characteristics(data: dict, unit_id_to_osw_id: dict, unit_entities_map: dict):
    """Create QuantityKind and Characteristic entities.

    Returns (quantity_kinds, fundamental_characteristics, non_fundamental_characteristics).
    """
    import opensemantic.core as _core
    import opensemantic.quantities as _quantities
    import opensemantic.characteristics.quantitative as _char_quant
    import types
    model = types.SimpleNamespace(
        **{k: v for m in [_core, _quantities, _char_quant]
           for k, v in vars(m).items() if not k.startswith("_")}
    )

    context = data["context"]
    id_dict = data["id_dict"]
    quantity_kinds = data["type_items"].get("qudt:QuantityKind", [])

    label_corrections = {
        "http://qudt.org/vocab/quantitykind/VaporPermeance": "VaporPermeance",
        "http://qudt.org/vocab/quantitykind/ConductivityVariance_NEON": "NEON Conductivity Variance",
        "http://qudt.org/vocab/quantitykind/TemperatureVariance_NEON": "NEON Temperature Variance",
        "http://qudt.org/vocab/quantitykind/EvaporativeHeatTransferCoefficient": "Evaporative Heat Transfer Coefficient",
    }
    hardcoded_fundamental = {
        "http://qudt.org/vocab/quantitykind/Frequency",
        "http://qudt.org/vocab/quantitykind/Radiance",
        "http://qudt.org/vocab/quantitykind/SpecificImpulseByWeight",
    }

    osw_quantity_list = []
    osw_fundamental_list = []
    osw_characteristic_list = []

    for qk in quantity_kinds:
        qk_id = qk.get("@id", "")
        full_uri = _resolve_curie(qk_id, context)

        applicable_units = _get_values(qk.get("qudt:applicableUnit", []), "@id")
        applicable_units = _expand_applicable_units(applicable_units, id_dict)
        applicable_units = sorted(applicable_units)  # deterministic iteration

        si_unit_osw_ids = [
            unit_id_to_osw_id[au_id]
            for au_id in applicable_units
            if au_id in unit_id_to_osw_id
        ]
        if not si_unit_osw_ids:
            continue

        labels = _sort_labels(_get_labels(qk))
        descriptions = _get_descriptions(qk)
        if not labels:
            continue

        for lbl in labels:
            if lbl.text:
                lbl.text = lbl.text[0].upper() + lbl.text[1:]

        if full_uri in label_corrections:
            labels[0] = model.Label(text=label_corrections[full_uri], lang=labels[0].lang)

        name = pascal_case(labels[0].text)

        close_matches = [full_uri]
        for match_key in ("qudt:dbpediaMatch", "qudt:siExactMatch"):
            val = qk.get(match_key)
            if val is None:
                continue
            if isinstance(val, list):
                for v in val:
                    if isinstance(v, dict):
                        m = v.get("@value", v.get("@id", ""))
                    elif isinstance(v, str):
                        m = v
                    else:
                        continue
                    if m:
                        close_matches.append(_resolve_curie(m, context))
            elif isinstance(val, dict):
                m = val.get("@value", val.get("@id", ""))
                if m:
                    close_matches.append(_resolve_curie(m, context))
            elif isinstance(val, str):
                close_matches.append(_resolve_curie(val, context))

        close_matches.sort()

        has_broader = "skos:broader" in qk
        is_fundamental = full_uri in hardcoded_fundamental or not has_broader

        if is_fundamental:
            qk_entity = model.QuantityKind(
                uuid=_make_uuid(full_uri),
                label=labels,
                description=descriptions,
                exact_ontology_match=[full_uri],
                close_ontology_match=close_matches,
                units=sorted(si_unit_osw_ids),
                name=name,
            )
            _sort_entity_arrays(qk_entity)
            osw_quantity_list.append(qk_entity)

            # Build unit_enumeration from enriched data
            unit_enum = []
            unit_cf = {}  # osw_id -> conversion factor
            seen_symbols = {}  # symbol -> osw_id (dedup QUDT duplicates)
            default_unit_id = None
            coherent_unit_id = None
            cf1_candidates = []  # (osw_id, symbol) pairs with cf=1.0
            for au_id in applicable_units:
                au_item = id_dict.get(au_id)
                if au_item is None or au_id not in unit_id_to_osw_id:
                    continue
                osw_id = unit_id_to_osw_id[au_id]
                symbol = au_item.get("qudt:symbol", au_id.split(":")[-1])
                # Deduplicate by symbol (QUDT has e.g. unit:FM and unit:FemtoM)
                if symbol in seen_symbols:
                    continue
                seen_symbols[symbol] = osw_id
                ucum_codes = _get_values(au_item.get("qudt:ucumCode", []), "@value")
                if not ucum_codes and isinstance(au_item.get("qudt:ucumCode"), str):
                    ucum_codes = [au_item["qudt:ucumCode"]]
                enum_name = _get_unit_enum_name(symbol, ucum_codes)
                if enum_name is None:
                    enum_name = _sanitize_identifier(symbol)
                unit_enum.append(model.UnitEnumerationElement(
                    osw_id=osw_id, name=enum_name, symbol=symbol,
                ))
                conv = au_item.get("qudt:conversionMultiplier", {})
                cf = conv.get("@value") if isinstance(conv, dict) else conv
                cf_float = float(cf) if cf is not None else float("inf")
                unit_cf[osw_id] = cf_float
                # Track coherent SI unit (qudt:derivedCoherentUnitOfSystem)
                coherent = au_item.get("qudt:derivedCoherentUnitOfSystem")
                if coherent:
                    coh_ids = [coherent] if isinstance(coherent, dict) else coherent
                    if any(c.get("@id") == "sou:SI" for c in coh_ids if isinstance(c, dict)):
                        coherent_unit_id = osw_id
                if cf_float == 1.0:
                    cf1_candidates.append((osw_id, symbol))
            # Pick default: coherent SI > shortest symbol among cf=1.0 > first
            if coherent_unit_id is not None:
                default_unit_id = coherent_unit_id
            elif cf1_candidates:
                # Prefer: no / or · (named), then shortest symbol, then alphabetical
                cf1_candidates.sort(key=lambda x: (
                    any(c in x[1] for c in "/·"),  # named units first
                    len(x[1]),                       # shorter symbol
                    x[1],                            # alphabetical tiebreak
                ))
                default_unit_id = cf1_candidates[0][0]
            if default_unit_id is None and si_unit_osw_ids:
                # Prefer base units (no # = not a prefixed subobject)
                base_units = [u for u in si_unit_osw_ids if "#" not in u]
                default_unit_id = base_units[0] if base_units else si_unit_osw_ids[0]

            # Sort: default unit first, then by conversion factor, then symbol
            if unit_enum:
                unit_enum.sort(
                    key=lambda ue: (
                        ue.osw_id != default_unit_id,
                        unit_cf.get(ue.osw_id, float("inf")),
                        ue.symbol,
                    )
                )

            quantity_property = f"Property:Has{name}Value"

            char = model.FundamentalQuantityValueType(
                subclass_of=["Category:OSW4082937906634af992cf9a1b18d772cf"],
                quantity=get_full_title(qk_entity),
                uuid=_make_uuid("characteristic:" + full_uri),
                description=descriptions,
                name=name,
                label=labels,
                close_ontology_match=close_matches,
                default_unit=default_unit_id,
                unit_enumeration=unit_enum if unit_enum else None,
                quantity_property=quantity_property,
            )
            osw_fundamental_list.append(char)
        else:
            broader_val = qk["skos:broader"]
            if isinstance(broader_val, list):
                broader_val = broader_val[0]
            broader_id = broader_val.get("@id", "") if isinstance(broader_val, dict) else broader_val
            broader_full_uri = _resolve_curie(broader_id, context)
            broader_char_uuid = _make_uuid("characteristic:" + broader_full_uri)
            broader_cat = f"Category:OSW{broader_char_uuid.replace('-', '')}"

            quantity_property = f"Property:Has{name}Value"

            char = model.QuantityValueType(
                subclass_of=[broader_cat],
                quantity=None,
                uuid=_make_uuid("characteristic:" + full_uri),
                description=descriptions,
                name=name,
                label=labels,
                close_ontology_match=close_matches,
                quantity_property=quantity_property,
            )
            osw_characteristic_list.append(char)

    for e in osw_quantity_list:
        _sort_entity_arrays(e)
    for e in osw_fundamental_list:
        _sort_entity_arrays(e)
    for e in osw_characteristic_list:
        _sort_entity_arrays(e)
    return osw_quantity_list, osw_fundamental_list, osw_characteristic_list


def _sort_json_arrays(obj):
    """Recursively sort list-of-strings for deterministic JSON output."""
    if isinstance(obj, dict):
        return {k: _sort_json_arrays(v) for k, v in obj.items()}
    if isinstance(obj, list):
        if all(isinstance(v, str) for v in obj):
            return sorted(obj)
        return [_sort_json_arrays(v) for v in obj]
    return obj


def postprocess_jsondata_files(package_dir: Path):
    """Sort string arrays in all slot_jsondata.json files for deterministic output.

    Only processes jsondata slots — jsonschema arrays have semantic ordering.
    """
    count = 0
    for json_file in package_dir.rglob("*.slot_jsondata.json"):
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        sorted_data = _sort_json_arrays(data)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(sorted_data, f, indent=4, ensure_ascii=False)
        count += 1
    print(f"Postprocessed {count} jsondata files in {package_dir}")
