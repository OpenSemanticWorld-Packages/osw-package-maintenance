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

## Python Code Generation

The generator (`tools/osw-python-package-generator/`) produces Pydantic v1 and v2 models from wiki JSON schemas.

Key settings (in `oold-python/src/oold/generator.py`):
- `use_title_as_name=True` — schema `title` becomes Python class name
- `reuse_model=True` — identical schemas should produce one class (has known limitations with cross-file resolution)
- `allof_class_hierarchy=Always` — `allOf` produces Python inheritance
- `field_include_all_keys=True` — custom keywords preserved in `json_schema_extra`

### Known Code Generator Limitations

1. **Duplicate classes from multiple `$ref` paths**: When the same schema is resolved via two different `$ref` chains, `reuse_model` may fail to deduplicate, producing `Tool` and `Tool1`. Not fixable via schema changes.

2. **`$ref` + custom keywords = new class**: When `items` has both `$ref` and inline custom keywords (e.g., `eval_template`), the merged result is treated as a distinct schema. Fix by moving shared keywords into the `$ref` target, or setting an explicit `title`.

## Cross-Package Dependencies

### Core → Base Boundary

5 core schemas reference 6 base schemas via `range`/`category`:
- ProcessType → Person
- Task → IssueLabel, Project, WorkPackage
- PhysicalItemType → OrganizationalUnit
- Process → Location, Person, Project
- File → Person

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

Use `$(variable_name)` syntax (not `{{variable_name}}`) for watch variable substitution in autocomplete queries:

```json
{
    "watch": { "characteristic_w": "channel.characteristic" },
    "options": {
        "autocomplete": {
            "query": "[[-HasUnit.-HasQuantity::$(characteristic_w)]][[HasSymbol::like:*{{_user_input}}*]]|?HasSymbol=label"
        }
    }
}
```

`{{_user_input}}` is a special built-in variable for the current autocomplete text input.

## Wiki Push Workflow

1. Edit schema files locally
2. Dry-run: `python scripts/push_package_changes.py packages/<name> --mode unstaged --dry-run`
3. Push staged: `python scripts/push_package_changes.py packages/<name> --mode staged -c "description"`
4. Verify on wiki
5. Bump version in packages.json, build script, and page package Item
6. Push page package Item to wiki
7. Commit to git, tag, push with tags

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

## Migration Scripts

For bulk data changes on the wiki, create scripts in `scripts/` using the osw-python API:
- `WtSite` + `CredentialManager` for auth
- `page.get_slot_content("jsondata")` returns dict
- `page.set_slot_content("jsondata", dict)` + `page.edit(comment="...")` to write
- Always default to dry-run mode (`--execute` flag to apply)
- Credentials file: `scripts/accounts.pwd.yaml` (imported via `reusable.py`)
