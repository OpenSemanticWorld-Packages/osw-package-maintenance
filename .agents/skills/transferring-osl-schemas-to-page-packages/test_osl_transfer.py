"""Tests for osl_transfer.py on synthetic fixtures.

Run from this folder: ``python -m unittest test_osl_transfer -v``
Each test builds a package git repository (package format: indent 4, CRLF, no final
newline, literal non-ASCII) and a source folder (indent 2, LF, final newline).
"""

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "osl_transfer.py"
_spec = importlib.util.spec_from_file_location("osl_transfer", TOOL)
osl = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(osl)

UUID = "2afce49f-e800-460a-95cf-480cc0656757"
OSW = "OSW" + UUID.replace("-", "")
CAT = f"base/Category/{OSW}"
PROP = "base/Property/HasTestLink"

JSONDATA = {
    "uuid": UUID,
    "name": "TestType",
    "type": ["Category:Category"],
    "label": [{"lang": "en", "text": "Test Type"}],
}
SCHEMA_REF = {
    "title": "TestType",
    "description*": {"de": "Prüfung"},
    "data_source_maps": [
        {
            "id": "pubchem.ncbi.nlm.nih.gov",
            "source": "https://x/{{cid}}",
            "label": "PubChem",
            "required": ["cid"],
            "object_map": {"a": "$.a"},
        }
    ],
    "required": ["type"],
    "defaultProperties": ["cid", "name"],
    "properties": {
        "cid": {"title": "CID", "type": "string"},
        "inchi": {
            "title": "InChI",
            "type": "array",
            "eval_template": [{"type": "mustache", "value": "{{inchi}}"}],
        },
    },
}
PROPDATA = {
    "uuid": "f0c91131-6d52-4de8-8b77-0e5fc6291047",
    "name": "HasTestLink",
    "type": ["Category:DataProperty"],
}
FOOTER = "line one\nline two"
NAMING = [
    "--suffix",
    ".jsondata.json=slot_jsondata.json",
    "--suffix",
    ".jsonschema.json=slot_jsonschema.json",
    "--suffix",
    ".footertemplate.txt=slot_footer_template.wikitext",
    "--name-prefix",
    "Property_=Property",
]


def write_package_file(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = (
        data
        if isinstance(data, str)
        else json.dumps(data, indent=4, ensure_ascii=False)
    )
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


def write_source_file(path, data):
    text = (
        data + "\n"
        if isinstance(data, str)
        else json.dumps(data, indent=2, sort_keys=True) + "\n"
    )
    path.write_bytes(text.encode("utf-8"))


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    )


class Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self._tmp.name)
        self.packages = root / "packages"
        self.pkg = self.packages / "world.test"
        write_package_file(self.pkg / f"{CAT}.slot_jsondata.json", JSONDATA)
        write_package_file(self.pkg / f"{CAT}.slot_jsonschema.json", SCHEMA_REF)
        write_package_file(self.pkg / f"{CAT}.slot_footer_template.wikitext", FOOTER)
        write_package_file(self.pkg / f"{PROP}.slot_jsondata.json", PROPDATA)
        git(self.pkg, "init", "-q")
        git(self.pkg, "config", "core.autocrlf", "false")
        git(self.pkg, "config", "user.email", "test@example.com")
        git(self.pkg, "config", "user.name", "test")
        git(self.pkg, "add", ".")
        git(self.pkg, "commit", "-q", "-m", "init")
        self.src = root / "src"
        self.src.mkdir()
        write_source_file(self.src / "TestType.jsondata.json", JSONDATA)
        write_source_file(self.src / "TestType.footertemplate.txt", FOOTER)
        write_source_file(self.src / "Property_HasTestLink.jsondata.json", PROPDATA)
        # source schema: PubChem map removed, ChemSpider map added, eval_template and "name" missing, new property
        src_schema = json.loads(json.dumps(SCHEMA_REF))
        src_schema["data_source_maps"] = [
            {
                "object_map": {"b": "$.b"},
                "required": ["csid"],
                "label": "ChemSpider",
                "source": "/api",
                "id": "chemspider",
            }
        ]
        del src_schema["properties"]["inchi"]["eval_template"]
        src_schema["defaultProperties"] = ["cid", "csid"]
        src_schema["properties"]["csid"] = {"title": "ChemSpider ID", "type": "string"}
        write_source_file(self.src / "TestType.jsonschema.json", src_schema)

    def tearDown(self):
        self._tmp.cleanup()

    def run_tool(self, cmd, *args, naming=NAMING):
        return subprocess.run(
            [sys.executable, str(TOOL), cmd, *naming, *map(str, args)],
            capture_output=True,
            text=True,
        )

    def merge(self, *options):
        return self.run_tool(
            "merge",
            "--src",
            self.src,
            "--packages",
            self.packages,
            "--ref",
            "HEAD",
            *options,
        )

    def schema_path(self):
        return self.pkg / f"{CAT}.slot_jsonschema.json"

    def all_decisions(self):
        return [
            "--keep",
            "TestType.jsonschema:properties.inchi.eval_template",
            "--allow-removal",
            "TestType.jsonschema:data_source_maps[id=pubchem.ncbi.nlm.nih.gov]",
            "--allow-removal",
            "TestType.jsonschema:defaultProperties",
        ]


class TestMapCompare(Fixture):
    def test_map_uses_uuid_and_property_name(self):
        out = self.run_tool(
            "map", "--src", self.src, "--packages", self.packages
        ).stdout
        self.assertIn(f"world.test/{CAT}.slot_jsonschema.json", out)
        self.assertIn(f"world.test/{CAT}.slot_footer_template.wikitext", out)
        self.assertIn(f"world.test/{PROP}.slot_jsondata.json", out)

    def test_compare_marks_source_only_ref_only_and_changed(self):
        out = self.run_tool(
            "compare", "--src", self.src, "--packages", self.packages, "--ref", "HEAD"
        ).stdout
        self.assertIn("L data_source_maps[id=chemspider]", out)
        self.assertIn("M data_source_maps[id=pubchem.ncbi.nlm.nih.gov]", out)
        self.assertIn("M properties.inchi.eval_template", out)
        self.assertIn('M defaultProperties (item "name")', out)
        self.assertIn('L defaultProperties (item "csid")', out)
        self.assertIn("L properties.csid", out)
        self.assertIn("TestType.jsondata.json: same", out)
        self.assertIn("TestType.footertemplate.txt: same", out)


class TestMerge(Fixture):
    def test_refuses_without_decisions_and_writes_nothing(self):
        before = self.schema_path().read_bytes()
        r = self.merge()
        self.assertEqual(r.returncode, 1)
        self.assertIn("NOTHING WRITTEN", r.stderr)
        for path in (
            "data_source_maps[id=pubchem.ncbi.nlm.nih.gov]",
            "properties.inchi.eval_template",
            'defaultProperties (item "name")',
        ):
            self.assertIn(path, r.stderr)
        self.assertEqual(self.schema_path().read_bytes(), before)

    def test_writes_package_format_and_ref_key_order(self):
        r = self.merge(*self.all_decisions())
        self.assertEqual(r.returncode, 0, r.stderr)
        raw = self.schema_path().read_bytes()
        self.assertEqual(
            raw.count(b"\n"), raw.count(b"\r\n"), "all line endings must be CRLF"
        )
        self.assertFalse(raw.endswith(b"\n"), "no final newline")
        text = raw.decode("utf-8")
        self.assertIn("Prüfung", text, "non-ASCII stays literal")
        self.assertTrue(text.split("\r\n")[1].startswith('    "'), "indent 4")
        data = json.loads(text)
        self.assertEqual(
            list(data), list(SCHEMA_REF), "top-level keys keep the ref order"
        )
        self.assertEqual(
            data["properties"]["inchi"]["eval_template"],
            SCHEMA_REF["properties"]["inchi"]["eval_template"],
        )
        self.assertEqual([m["id"] for m in data["data_source_maps"]], ["chemspider"])
        # a new list item takes its key order from the first sibling at the ref
        self.assertEqual(
            list(data["data_source_maps"][0]),
            ["id", "source", "label", "required", "object_map"],
        )
        # a new key follows its predecessor in the source order (source keys are sorted: cid, csid, inchi)
        self.assertEqual(list(data["properties"]), ["cid", "csid", "inchi"])

    def test_keeps_one_list_item_next_to_source_items(self):
        r = self.merge(
            "--keep",
            "TestType.jsonschema:properties.inchi.eval_template",
            "--keep",
            "TestType.jsonschema:data_source_maps[id=pubchem.ncbi.nlm.nih.gov]",
            "--allow-removal",
            "TestType.jsonschema:defaultProperties",
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(self.schema_path().read_bytes())
        self.assertEqual(
            [m["id"] for m in data["data_source_maps"]],
            ["chemspider", "pubchem.ncbi.nlm.nih.gov"],
        )

    def test_drop_leaves_source_content_out(self):
        r = self.merge(
            *self.all_decisions(), "--drop", "TestType.jsonschema:properties.csid"
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(
            "csid", json.loads(self.schema_path().read_bytes())["properties"]
        )

    def test_unchanged_files_are_not_written(self):
        jsondata = self.pkg / f"{CAT}.slot_jsondata.json"
        footer = self.pkg / f"{CAT}.slot_footer_template.wikitext"
        before = (jsondata.read_bytes(), footer.read_bytes())
        r = self.merge(*self.all_decisions())
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("unchanged", r.stdout)
        self.assertEqual((jsondata.read_bytes(), footer.read_bytes()), before)
        changed = [
            line
            for line in git(self.pkg, "status", "--porcelain").stdout.splitlines()
            if line
        ]
        self.assertEqual(changed, [f" M {CAT}.slot_jsonschema.json"])

    def test_text_file_keeps_crlf_and_missing_final_newline(self):
        write_source_file(
            self.src / "TestType.footertemplate.txt", FOOTER + "\nline three"
        )
        r = self.merge(*self.all_decisions())
        self.assertEqual(r.returncode, 0, r.stderr)
        raw = (self.pkg / f"{CAT}.slot_footer_template.wikitext").read_bytes()
        self.assertEqual(raw, b"line one\r\nline two\r\nline three")

    def test_refuses_when_working_tree_differs_from_ref(self):
        path = self.pkg / f"{PROP}.slot_jsondata.json"
        write_package_file(
            path, dict(PROPDATA, description=[{"lang": "en", "text": "local edit"}])
        )
        r = self.merge(*self.all_decisions())
        self.assertEqual(r.returncode, 1)
        self.assertIn("working tree differs", r.stderr)
        r = self.merge(*self.all_decisions(), "--allow-dirty")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn("local edit", path.read_text(encoding="utf-8"))

    def test_page_in_two_packages_is_an_error(self):
        other = self.packages / "world.other"
        write_package_file(other / f"{CAT}.slot_jsondata.json", JSONDATA)
        r = self.run_tool("map", "--src", self.src, "--packages", self.packages)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("more than one package", r.stderr)


class TestNaming(Fixture):
    def test_requires_one_jsondata_suffix(self):
        r = self.run_tool(
            "map",
            "--src",
            self.src,
            "--packages",
            self.packages,
            naming=["--suffix", ".jsonschema.json=slot_jsonschema.json"],
        )
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("slot_jsondata.json", r.stderr)

    def test_rejects_invalid_package_suffix(self):
        r = self.run_tool(
            "map",
            "--src",
            self.src,
            "--packages",
            self.packages,
            naming=[
                "--suffix",
                ".jsondata.json=slot_jsondata.json",
                "--suffix",
                ".x.json=jsondata.json",
            ],
        )
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("slot_<slot>.<ext>", r.stderr)

    def test_custom_source_suffixes(self):
        for f in list(self.src.iterdir()):
            f.rename(
                f.with_name(
                    f.name.replace(".jsondata.json", ".jd.json").replace(
                        ".jsonschema.json", ".js.json"
                    )
                )
            )
        naming = [
            "--suffix",
            ".jd.json=slot_jsondata.json",
            "--suffix",
            ".js.json=slot_jsonschema.json",
            "--name-prefix",
            "Property_=Property",
        ]
        out = self.run_tool(
            "compare",
            "--src",
            self.src,
            "--packages",
            self.packages,
            "--ref",
            "HEAD",
            naming=naming,
        ).stdout
        self.assertIn("TestType.jd.json: same", out)
        self.assertIn("M properties.inchi.eval_template", out)
        self.assertIn("Property_HasTestLink.jd.json: same", out)
        r = self.run_tool(
            "merge",
            "--src",
            self.src,
            "--packages",
            self.packages,
            "--ref",
            "HEAD",
            *self.all_decisions(),
            naming=naming,
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        data = json.loads(self.schema_path().read_bytes())
        self.assertEqual(
            data["properties"]["inchi"]["eval_template"],
            SCHEMA_REF["properties"]["inchi"]["eval_template"],
        )

    def test_file_matches_only_its_longest_suffix(self):
        pages = osl.source_pages(
            self.src,
            {".json": "slot_jsonschema.json", ".jsondata.json": "slot_jsondata.json"},
        )
        self.assertIn("TestType", pages)
        self.assertNotIn("TestType.jsondata", pages)
        self.assertEqual(set(pages["TestType"]), {".jsondata.json"})

    def test_longest_name_prefix_wins(self):
        f = self.src / "Property_HasTestLink.jsondata.json"
        for prefixes in (
            {"P": "Item", "Property_": "Property"},
            {"Property_": "Property", "P": "Item"},
        ):
            self.assertEqual(
                osl.page_file_base("Property_HasTestLink", f, prefixes),
                ("Property", "HasTestLink"),
            )

    def test_without_name_prefix_property_is_looked_up_by_uuid(self):
        out = self.run_tool(
            "map",
            "--src",
            self.src,
            "--packages",
            self.packages,
            "Property_HasTestLink",
            naming=NAMING[:6],
        ).stdout
        self.assertNotIn(PROP, out)
        self.assertIn("NOT FOUND", out)


class TestDropAndFormat(unittest.TestCase):
    def test_drop_keeps_source_format_and_handles_dots_in_selector(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "schema.json"
            data = {"data_source_maps": [{"id": "a.b.c"}, {"id": "keep"}], "t": "ä"}
            path.write_bytes((json.dumps(data, indent=2) + "\n").encode("utf-8"))
            r = subprocess.run(
                [
                    sys.executable,
                    str(TOOL),
                    "drop",
                    str(path),
                    "--path",
                    "data_source_maps[id=a.b.c]",
                ],
                capture_output=True,
                text=True,
            )
            self.assertEqual(r.returncode, 0, r.stderr)
            expected = (
                json.dumps({"data_source_maps": [{"id": "keep"}], "t": "ä"}, indent=2)
                + "\n"
            )
            self.assertEqual(path.read_bytes(), expected.encode("utf-8"))

    def test_detect_format_escapes_outside_u00(self):
        text = json.dumps({"a": "μ", "b": "–"}, indent=4)
        fmt = osl.detect_format(text)
        self.assertTrue(fmt["ensure_ascii"])
        self.assertEqual(osl.dump_json(json.loads(text), fmt), text)

    def test_detect_format_literal_non_ascii(self):
        fmt = osl.detect_format('{\r\n    "a": "ü"\r\n}')
        self.assertEqual(
            fmt,
            {
                "indent": 4,
                "newline": "\r\n",
                "final_newline": False,
                "ensure_ascii": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
