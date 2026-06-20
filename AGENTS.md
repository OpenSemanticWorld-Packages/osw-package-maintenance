# Schema Creation and Editing Guidelines

## Package Structure

Each OSW schema package lives under `packages/<package-name>/` with this layout:

```
packages/world.opensemantic.<name>/
  packages.json          # Package metadata, version, required packages
  <subdir>/              # "core" for core, "base" for base, etc.
    Category/
      <OSW-ID>.slot_jsondata.json
      <OSW-ID>.slot_jsonschema.json
      <OSW-ID>.slot_schema_template.text   # Handlebars (if applicable)
      <OSW-ID>.slot_main.wikitext
      <OSW-ID>.slot_header.wikitext
      <OSW-ID>.slot_footer.wikitext
    Property/
      <Name>.slot_jsondata.json
      <Name>.slot_jsonschema.json
      <Name>.slot_main.wikitext
      <Name>.slot_header.wikitext
      <Name>.slot_footer.wikitext
    Item/
      <OSW-ID>.slot_jsondata.json
      ...
    JsonSchema/
      <Name>.slot_main.json
    Template/
      <Path>.slot_main.wikitext
```

Build scripts live at `scripts/world.opensemantic.<name>.py` and list all page titles belonging to the package.

## JSON Schema Conventions

### Inline Sub-objects: Always Set a `title`

When defining inline sub-objects (objects in `items`, `properties`, or `oneOf`), always set a meaningful, unique `title`. The Python code generator uses `title` as the class name via `use_title_as_name=True`.

**Bad** — generates collisions like `LabelItem`, `Tool1`, `IDAndCountry1`:
```json
{
  "items": {
    "type": "object",
    "properties": { ... }
  }
}
```

**Good** — generates a clean, predictable class name:
```json
{
  "items": {
    "title": "MaterialConstituent",
    "type": "object",
    "properties": { ... }
  }
}
```

Rules for inline `title`:
- Use PascalCase, no spaces (it becomes the Python class name directly)
- Make it specific to the context: `MaterialConstituent` not `Constituent`, `InstitutePostalAddress` not `PostalAddress`
- Empty `"title": ""` is worse than no title — it causes unpredictable naming. Always set a meaningful value.
- When two inline sub-objects in different schemas share the same human-friendly name (e.g., both called "Factor"), set a context-specific PascalCase `title` to distinguish them for code generation, and move the original display name to `title*` so it's still shown in the wiki editor:
```json
{
  "items": {
    "title": "QuantityUnitFactor",
    "title*": {"en": "Factor", "de": "Faktor"},
    "type": "object",
    "properties": { ... }
  }
}
```
Without distinct `title` values, the code generator produces numbered collisions like `Factor` and `Factor1`.

### Shared Schemas via `$ref`

Reusable sub-schemas live in `JsonSchema:` pages (e.g., `JsonSchema:Label`, `JsonSchema:Description`).

When using `$ref` alongside custom keywords:

**Prefer**: Move custom keywords INTO the `$ref` target when they're identical across all usages:
```json
// In JsonSchema:Label (shared definition)
{
  "title": "Label",
  "eval_template": [{"type": "wikitext", "mode": "store", "value": "{{{text}}}@{{{lang}}}"}],
  "properties": { ... }
}

// In Entity.slot_jsonschema.json (consumer)
{
  "label": {
    "items": {
      "$ref": "/wiki/JsonSchema:Label?action=raw"
    }
  }
}
```

**Only when overriding**: Keep custom keywords alongside `$ref` and set a distinct `title`:
```json
{
  "short_name": {
    "items": {
      "$ref": "/wiki/JsonSchema:Label?action=raw",
      "title": "ShortName",
      "title*": {"de": "Kurzname"}
    }
  }
}
```

This ensures the code generator produces a named subclass rather than a collision like `LabelItem1`.

### `range` and `category` References

The `range` keyword specifies which Category an autocomplete field targets. The oold-python preprocessor converts `range` to `$ref`, which pulls in the target schema as a Python type annotation.

Be aware that `range`/`category` references create **structural dependencies** in generated Python code. A `range` pointing to a schema in another package will pull that schema (and all its transitive dependencies) into the generated module.

### Custom Keywords

Non-standard JSON Schema keywords (`eval_template`, `title*`, `description*`, `options`, `watch`, `dynamic_template`, `range`, `category`, etc.) are preserved in `json_schema_extra` during Python code generation and re-injected during schema export. This is intentional — schema-to-code must be reversible.

When two schemas share the same `$ref` but differ in custom keywords, the code generator correctly treats them as distinct types. To control naming, always set an explicit `title` on such merged schemas.

### `allOf` Inheritance

Schemas inherit from parent schemas via `allOf` with `$ref`:
```json
{
  "allOf": [
    {"$ref": "/wiki/Category:OSW...?action=raw&slot=jsonschema"}
  ]
}
```

The code generator converts these to Python class inheritance. Each `allOf` entry becomes a base class.

### Property Ordering

Use `propertyOrder` to control field position in the wiki editor. Lower values appear first. Convention:
- `type`: `-1010`
- `subclass_of`: `-1009`
- `label`: `-1008`

### Version Management

Version is tracked in **three** places that must be updated together:
1. `packages.json` (`"version"` field)
2. Build script (`scripts/world.opensemantic.<name>.py`, `version=` parameter)
3. Page package Item (`base/Item/OSW<id>.slot_jsondata.json`, `"version"` field)

Workflow:
- Use semantic versioning: bump patch for fixes, minor for new schemas, major for breaking changes
- After bumping, push the page package Item to the wiki before committing to git
- Run `python scripts/sync_package_tags.py --packages <name> --apply` to create git tags from version history
- Push tags with `git push origin --tags` from within the package submodule

## Wiki Push Workflow

1. Edit schema files locally
2. Dry-run: `python scripts/push_package_changes.py packages/<name> --mode unstaged --dry-run`
3. Push staged: `python scripts/push_package_changes.py packages/<name> --mode staged -c "description"`
4. Verify on wiki
5. Bump version in packages.json, build script, and page package Item
6. Push page package Item to wiki
7. Commit to git, tag, push with tags

Notes:
- **New pages** (not yet in `packages.json`): `push_package_changes.py` derives the page title and slots from the file path, so brand-new pages push correctly. `git add` them and use `--mode staged`. **Push new pages BEFORE rebuilding the package** - the build's `create()` (with `prefer_local_pages=False`) deletes the package subdir and re-fetches from the wiki, which wipes local-only pages.
- **Other wikis / credentials**: `-d <domain>` selects the target wiki; `--cred-filepath <path>` points at a specific `accounts.pwd.yaml`.
- **Protected namespaces** (often `Category`): the push account needs the right that `$wgNamespaceProtection` requires; for a bot login the matching **bot-password grant** must also be set (effective rights = user rights AND bot-password grants). Otherwise create the page manually.

## Python Code Generation

The generator (`tools/osw-python-package-generator/`) produces Pydantic v1 and v2 models from JSON schemas.

Key settings (in `oold-python/src/oold/generator.py`):
- `use_title_as_name=True` - schema `title` becomes Python class name
- `reuse_model=True` - identical schemas should produce one class (has known limitations with cross-file resolution)
- `allof_class_hierarchy=Always` - `allOf` produces Python inheritance
- `field_include_all_keys=True` - custom keywords preserved in `json_schema_extra`

The generator auto-downloads the upstream `*-python` dependency packages from GitHub (latest tag) for class deduplication, so no local sibling checkout is required. It requires `osw>=1.1.2` - earlier versions corrupt the generated `# filename:` header comments, rewriting the OSW-ID to the class name (e.g. `# filename: OSW<id>.json` becomes `# filename: <ClassName>.json`).

### Known Code Generator Limitations

1. **Duplicate classes from multiple `$ref` paths**: When the same schema is resolved via two different `$ref` chains, `reuse_model` may fail to deduplicate, producing `Tool` and `Tool1`. Not fixable via schema changes.

2. **`$ref` + custom keywords = new class**: When `items` has both `$ref` and inline custom keywords (e.g., `eval_template`), the merged result is treated as a distinct schema. Fix by moving shared keywords into the `$ref` target, or setting an explicit `title`.

## Cross-Package Dependencies

### Core - Base Boundary

5 core schemas reference 6 base schemas via `range`/`category`:
- ProcessType - Person
- Task - IssueLabel, Project, WorkPackage
- PhysicalItemType - OrganizationalUnit
- Process - Location, Person, Project
- File - Person

These 6 direct dependencies pull in 20 base schemas transitively (Person -> PersonRole, Competence, etc.), which is why the core Python package contains ~120 classes instead of the expected ~38. Process-related schemas (ProcessType, Process, Task, PhysicalItemType, PhysicalItem, Tool, StatusEnumeration, TaskStatus, Priority, ToolMaintenanceEvent) were moved from core to base to reduce this coupling.

When moving schemas between packages, check for `range`/`category` references that would create new cross-package dependencies: `grep -r '"range"\|"category"' packages/<name>/`.

### Package Merge Checklist

When merging package A into package B:
1. Copy slot files from A's subdir to B's subdir (Category/, Property/, etc.)
2. Add page titles to B's build script
3. Update `requiredPackages` in all scripts that depended on A → point to B
4. Update file paths in any scripts that read A's local files
5. Mark A as archived in its `packages.json` description and build script
6. Do NOT copy A's package Item (the PagePackage entity) — it stays with A

### CharacteristicType Schema (oneOf Pattern)

The CharacteristicType uses a flat 5-entry `oneOf` discriminated by `type`:

| Entry | `type` value | Purpose |
|-------|-------------|---------|
| NumberProperty | `"number"` or `"integer"` | Numeric values |
| TextProperty | `"string"` | Text values |
| BooleanProperty | `"boolean"` | Boolean values |
| LinkProperty | `"iri"` | Autocomplete references |
| ComplexProperty | `"object"` | Nested characteristics |

When creating new CharacteristicType instances, each property in the `properties` array MUST have a `type` field matching one of these discriminators. The old `property_type` field (`SimpleProperty`, `ComplexProperty`, etc.) is deprecated.

#### How the Schema Template Maps Properties to JSON Schema

The Handlebars template (`slot_schema_template.text`) transforms each entry in the jsondata `properties` array into a JSON Schema property. Key mapping rules:

1. **Primitive types** (`type: "number"`, `"string"`, `"boolean"`, `"integer"`): emit `"type": "<value>"` directly
2. **Link/autocomplete** (`range` is set): emit `"type": "string", "format": "autocomplete", "range": "<category>"`
3. **Complex/nested characteristic** (`characteristic` is set, `type: "object"`): emit `"$ref": "/wiki/<characteristic>?action=raw&slot=jsonschema"` — the `$ref` pulls in the characteristic's generated schema (which includes its own properties, type defaults, allOf chain, etc.)
4. **RDF property mapping** (`rdf_property` is set): emit `"$ref": "/wiki/<rdf_property>?action=raw&slot=jsonschema"`

**Important**: When `characteristic` is present, `type` is NOT emitted — the `$ref` to the characteristic schema provides the full type structure. When manually writing schemas that reference a characteristic (outside the template), use `$ref` directly:

```json
{
  "sampling_interval": {
    "title": "Sampling interval",
    "title*": {"de": "Abtastintervall"},
    "$ref": "/wiki/Category:OSW389cb87d31be515aa5d2f12e2b66e938?action=raw&slot=jsonschema"
  }
}
```

Do NOT use `"type": "object", "characteristic": "Category:..."` in hand-written schemas — `characteristic` is a jsondata field that the template converts to `$ref`. In the jsonschema slot, always use `$ref` directly.

### `{{#ifexist:}}` vs SMW Queries for Page Existence

MediaWiki's `{{#ifexist:}}` is cached aggressively and counts as an expensive parser function. For checking if a package dependency is installed, prefer SMW queries:

```wikitext
{{#if: {{#ask: [[:Category:OSW...]] |?HasName= |mainlabel=-}} | (exists) | (missing) }}
```

This checks if the category page exists AND has jsondata, which is a more reliable indicator of package installation.

### Watch Variables in Autocomplete Queries

The autocomplete query string is processed in three steps by `MwJson_editor.js search_smw`:

1. **`{{$(key)}}` replacement**: replaced with `{{watched_path}}`, then resolved by Handlebars from jsondata
2. **`$(key)` replacement**: replaced with the **resolved watch value** directly (no Handlebars). Undefined values become `+` (SMW wildcard)
3. **Handlebars evaluation**: the query is compiled as a Handlebars template with jsondata as context

Built-in Handlebars variables: `{{_user_input}}`, `{{_user_input_normalized}}`, `{{_user_lang}}`.

**When to use which form:**

- `{{field}}` - when the field exists directly in the page's jsondata (e.g., `{{quantity}}` on a FundamentalQuantityValueType instance that has `quantity` in its jsondata)
- `$(watch_var)` - when the value comes from a watch path, especially from `root.*` paths (e.g., `$(parent_w)` watching `root.subclass_of.0`)
- `{{$(watch_var)}}` - **required inside array item schemas** where the watch uses a relative path via an `id` anchor. Handlebars cannot resolve these from the root jsondata; the `{{$()}}` substitution first resolves the watch variable, then Handlebars processes the result.

**Array-relative watch paths with `id` anchors:**

Inside array `items`, set `"id": "<anchor>"` to create a named reference point. Watch paths can then use `<anchor>.<field>` to reference sibling fields within the same array element:

```json
{
    "data_channels": {
        "type": "array",
        "items": {
            "id": "channel",
            "properties": {
                "characteristic": { "type": "string", "format": "autocomplete" },
                "unit": {
                    "watch": { "characteristic_w": "channel.characteristic" },
                    "options": {
                        "autocomplete": {
                            "query": "[[-HasUnit.-HasQuantity::{{$(characteristic_w)}}]][[HasSymbol::like:*{{_user_input}}*]]|?HasSymbol=label"
                        }
                    }
                }
            }
        }
    }
}
```

Here `channel.characteristic` resolves to the `characteristic` field of the **current** array element (not `root.data_channels.?.characteristic`, which is not supported). The `{{$(characteristic_w)}}` form is needed because Handlebars alone cannot resolve the watch variable - it only has access to the root jsondata context.

### Template-time vs Editor-time Variables

See full documentation: https://opensemantic.world/wiki/Item:OSWab674d663a5b472f838d8e1eb43e6784

Two distinct variable scopes exist:

**Schema template variables** (resolved when a Category page is saved, producing the static jsonschema via `slot_schema_template.text`):
- `{{{_current_subject_}}}` - title/OSW-ID of the current page/entry (preferred)
- `{{{_page_title}}}` - deprecated, use `_current_subject_` instead
- `{{{name}}}`, `{{{uuid}}}`, `{{{label}}}`, etc. - jsondata fields of the Category
- `{{{subclass_of.[0]}}}` - first entry of the subclass_of array
- `{{> self}}` - template itself as partial (enables recursion)

**Editor-time variables** (resolved at runtime when a user edits an instance):
- `{{{_current_subject_}}}` - the page being edited (in `dynamic_template` context)
- `{{{_current_user_}}}` - active user identity (e.g., `User:MyUserName`)
- `{{{_array_index_}}}` - array item position within parent
- `{{{_global_index_}}}` - smallest non-existing prefixed index for property values
- `$(watch_var)` - watch variable substitution (from `"watch": {"watch_var": "root.field"}`)
- `{{_user_input}}` - current text in an autocomplete input field
- `{{_user_input_normalized}}` - normalized user input for query matching
- `{{_user_lang}}` - current user language preference
- `root.field.0` - can be used in watch paths to reference array elements

### Autocomplete Query Shortcuts

The editor supports shorthand keywords for common autocomplete patterns:

- **`category`**: populates field with instances of the given category (and subcategories)
  ```json
  { "options": { "autocomplete": { "category": "Category:X" } } }
  ```
- **`subclassof_range`**: targets subclasses of the given category. The inline editor uses the meta class of the given category.
  ```json
  { "options": { "autocomplete": { "subclassof_range": "Category:Device" } } }
  ```
- **Custom `query`**: full SMW query with handlebars template variables

Autocomplete automatically appends `|?Display_title_of=label|?HasImage=image|?HasDescription=description|limit=100` unless user-specified.

### SMW Inverse Property Chains

In SMW property chain syntax, `-PropertyName` means inverse (follow the link backwards). Chain direction reads right-to-left from the query value:

`[[-HasUnit.-HasQuantity.-SubClassOf::X]]` reads as:
- X <- SubClassOf <- R (R is what X is a subclass of)
- R <- HasQuantity <- Q (Q is the QuantityKind that R has)
- Q <- HasUnit <- P (P is a Unit of Q) - P is the result

Common patterns for finding units of a characteristic's parent:
```json
{
    "watch": { "parent_w": "root.subclass_of.0" },
    "options": {
        "autocomplete": {
            "query": "[[-HasUnit.-HasQuantity::$(parent_w)]][[HasSymbol::like:*{{_user_input}}*]]OR[[-HasUnit.-HasQuantity.-SubClassOf::$(parent_w)]][[HasSymbol::like:*{{_user_input}}*]]OR[[-HasUnit.-HasQuantity.-SubClassOf.-SubClassOf::$(parent_w)]][[HasSymbol::like:*{{_user_input}}*]]|?HasSymbol=label"
        }
    }
}
```

Note: The first OR clause queries the parent directly (it may have HasQuantity itself). Subsequent clauses traverse the inverse SubClassOf chain upward. SMW has query depth limits - 3 levels of `-SubClassOf` nesting is typically the maximum before hitting wiki restrictions.

### Undocumented Behaviors (not in online docs)

These behaviors were discovered empirically and are not yet in the official documentation:

1. **`subclassof_range` does not include the category itself** in query results - only subclasses. To include the category page itself, add an explicit `OR` clause: `[[:Category:OSW...]]OR[[SubClassOf::Category:OSW...]]`

2. **Watch path array indexing**: `"root.subclass_of.0"` accesses the first element of an array field. This is not documented but works in practice.

3. **SMW query depth limits**: Inverse property chains with more than ~3 levels of nesting (`-SubClassOf.-SubClassOf.-SubClassOf`) hit wiki query depth/size restrictions. The wiki returns an error about query conditions that could not be considered. Keep chains to 3 levels maximum.

4. **`{{{_page_title}}}`** is deprecated in schema templates - use `{{{_current_subject_}}}` instead. Both resolve to the Category page title at template evaluation time.

5. **`format: "table"`** on array properties renders items in a compact table layout instead of the default collapsible "Category 1", "Category 2" headers which create visual overhead.

6. **`$comment`** is preserved in JSON Schema but ignored by the editor and code generator. Use it for documentation purposes within schemas.

7. **`options.hidden: true`** hides a property from the default editor view. Useful for deprecated fields that should not be removed (to avoid breaking existing data) but should not be shown to users.

## Python Code Generation Workflow

The generator (`tools/osw-python-package-generator/`) produces Pydantic v1 and v2 models from JSON schemas for each schema package.

### Building Python packages

1. Edit `tools/osw-python-package-generator/examples/build_package.py` to enable the desired packages
2. Run from the generator's `.venv`:
   ```bash
   cd tools/osw-python-package-generator
   .venv/Scripts/python examples/build_package.py
   ```
3. Verify generated code:
   - Check class counts match between v1 and v2: `grep -c "^class " python_packages/<pkg>/src/opensemantic/<name>/_model.py`
   - Scan for collision classes: `grep -n "^class " <file> | grep -E "[0-9]$"`
   - Compare v1 vs v2 class lists for divergence
4. The generator downloads schema packages from GitHub by tag (e.g., `v0.42.8`), so ensure tags are pushed before building

### Output structure

Each Python package is generated at:
```
python_packages/opensemantic.<name>-python/
  src/opensemantic/<name>/
    _model.py          # Pydantic v2 models
    v1/_model.py       # Pydantic v1 models
    _controller.py     # (manual) Controller logic
```

### Deduplication across packages

The generator removes classes that already exist in dependency packages and replaces them with imports. For example, `opensemantic.base-python` imports `Entity`, `Item`, `Category` etc. from `opensemantic.core-python` instead of regenerating them.

## Adding a New Custom Quantity

A custom quantity (one NOT in QUDT, e.g. a derived/slope quantity) needs four
artifacts, created bottom-up. Worked example: "Steigung der Wärmeleitfähigkeit"
(slope of a thermal conductance over time, unit `W/(K·h)`) in a project package.

This is the proper path when the quantity has a **new dimension/unit**. (If you
only need a unit variant of an existing fundamental quantity - e.g. a pressure
limit in bar - don't do all this: just `subclass_of` the existing characteristic
and override `default_unit`, reusing its `unit_enumeration`.)

### Reference category/type OSW-IDs

| Role | Type to put in the page's `type` (or `subclass_of`/`metaclass`) |
|------|------|
| Unit (composed) | `Category:OSW6c2aea028a8647cd97f5d7c65c09cd44` |
| Scaled/prefixed unit subobject (in `composed_units`) | `Category:OSW6ef70c808fb54abbbacb059c285713d4` |
| QuantityKind | `Category:OSW00fbd6feecb5408997ca18d4e681a131` |
| Characteristic (FundamentalQuantityValueType) | `type`: `Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7` |
| Characteristic parent | `subclass_of`: `Category:OSW4082937906634af992cf9a1b18d772cf` |
| Characteristic metaclass (holds the schema template) | `metaclass`: `Category:OSWac07a46c2cf14f3daec503136861f5ab` |
| Quantity Property | `Category:OSW1b15ddcf042c4599bd9d431cbfdf3430` |

Common base unit Items: Watt `Item:OSW58b03da1b2d35d8ca09043abb7fc8870`,
Kelvin `Item:OSWe728730c00ea5cf9af66a550e51b9717`,
Metre `Item:OSWf101d25e944856e3bd4b4c9863db7de2`,
Second `Item:OSW85302b21cf045998b80f38c9fdb88f84`,
Hour `Item:OSWa58b950af5d658e7b8bc2e1736817e43`.

### 1. Unit(s) - Item

Model the **SI-coherent base unit** (`conversion_factor_from_si: 1.0`) with
`factor_units` built from **named QUDT unit Items** (W, K, s, ... - not a
base-unit decomposition; that matches every existing composed unit). Add
non-coherent units (e.g. per-hour) and metric prefixes as scaling subobjects in
a `composed_units` array, each with its own `conversion_factor_from_si`,
`main_symbol`, `ucum_codes`, and `factor_units`. `conversion_factor_from_si` =
how many SI base units are in one of this unit (product of the factor units'
factors ^ exponents; e.g. `W/(K·h)` = `1·1·3600⁻¹` = `1/3600`).

A scaling subobject's `osw_id` is `Item:OSW<base>#OSW<sub>`.

### 2. Quantity - Item (QuantityKind)

`type: [Category:OSW00fbd6feecb5408997ca18d4e681a131]`, with
`units: [Item:OSW<base unit>]`.

### 3. Characteristic - Category (FundamentalQuantityValueType)

```json
{
  "type": ["Category:OSWc7f9aec4f71f4346b6031f96d7e46bd7"],
  "subclass_of": ["Category:OSW4082937906634af992cf9a1b18d772cf"],
  "metaclass": ["Category:OSWac07a46c2cf14f3daec503136861f5ab"],
  "quantity": "Item:OSW<quantitykind>",
  "default_unit": "Item:OSW<base>#OSW<sub>",
  "unit_enumeration": [{"osw_id": "...", "name": "...", "symbol": "..."}],
  "quantity_property": "Property:Has<Name>Value"
}
```
The `slot_jsonschema.json` is generated by the metaclass template on save -
push the jsondata and let the wiki regenerate it, then pull it back. The
editor `default_unit` may be a non-SI unit (the template supports this).

### 4. Property - Property

`type: [Category:OSW1b15ddcf042c4599bd9d431cbfdf3430]`, `property_type: "Quantity"`,
`main_unit` = the SI unit (`conversion_factor_to_main_unit: "1.0"`), plus
`additional_units` (factor = this-unit number / main-unit number; e.g. `W/(K·h)`
relative to main `W/(K·s)` = `3600`).

### Slots per page

Item/Property: `slot_jsondata.json` + `slot_main.wikitext` (empty) +
`slot_header.wikitext` (`{{#invoke:Entity|header}}`) +
`slot_footer.wikitext` (`{{#invoke:Entity|footer}}`). Category additionally has
`slot_jsonschema.json`.

### UUIDs

Stable, reproducible UUIDs are `uuid5(uuid.NAMESPACE_URL, <canonical string>)`
(`scripts/enriched_qudt.py::_make_uuid`):
- Unit: the full IRI, e.g. `http://qudt.org/vocab/unit/W-PER-K`
- Factor-unit subobject: `{unit_curie}#factorUnit#{factor_curie}#{exp}` (e.g. `unit:W-PER-K#factorUnit#unit:W#1`)
- QuantityKind: `http://qudt.org/vocab/quantitykind/<Name>`
- Characteristic: `characteristic:` + the QK IRI
- Property: `property:` + name

For a one-off custom quantity not destined for QUDT, a random `uuid4` is fine.

### Build, push, release

1. Add the four page titles to the package build script's `page_titles`.
2. **Push the new pages to the wiki BEFORE running the schema build.** Use
   `push_package_changes.py --mode staged` - it supports pages not yet in
   `packages.json` (derives the page from the file path). Reason: the schema
   build's `create()` with `prefer_local_pages=False` **deletes the package
   subdir and re-fetches from the wiki**, which would wipe local-only pages.
   - The `Category` namespace is often protected. The push account (and its
     **bot-password grant**, separately) needs the right `$wgNamespaceProtection`
     requires; otherwise create the Category page manually.
3. Bump the version (build script `version=` and the page-package Item) - minor
   bump for new schemas.
4. Run the build script to regenerate `packages.json` and push the page-package
   Item to the wiki (now non-destructive, since the pages exist on the wiki).
5. Commit the schema package, tag `vX.Y.Z`, push (commit + tag).
6. Regenerate the Python package (`<pkg>-python.py`): the generator downloads
   the schema by tag, so the tag must be pushed first. Commit, tag
   `v<schema>.post<build>`, push.

## Migration Scripts

For bulk data changes on the wiki, create scripts in `scripts/` using the osw-python API:
- `WtSite` + `CredentialManager` for auth
- `page.get_slot_content("jsondata")` returns dict
- `page.set_slot_content("jsondata", dict)` + `page.edit(comment="...")` to write
- Always default to dry-run mode (`--execute` flag to apply)
- Credentials file: `scripts/accounts.pwd.yaml` (imported via `reusable.py`)
