# SPDX-License-Identifier: Apache-2.0
"""Synthetic regression coverage for deterministic product CSV imports."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from importers.csv_products import MappingError, import_products, validate_mapping

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_csv.py"


def mapping(**overrides):
    base = {
        "version": 1,
        "resource": "product",
        "store_id": "store_demo",
        "source_namespace": "catalog-demo",
        "delimiter": ";",
        "encoding": "utf-8-sig",
        "decimal_separator": ",",
        "currency": "EUR",
        "columns": {"external_id": "ref", "name": "label", "sku": "sku", "barcode": "barcode", "sale_price": "price"},
    }
    base.update(overrides)
    return base


class CsvProductsTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    def csv(self, contents: str):
        path = self.directory / "items.csv"
        path.write_text(contents, encoding="utf-8-sig")
        return path

    def test_zero_price_is_not_missing_and_sku_preserves_zeros(self):
        source = self.csv("ref;label;sku;barcode;price\nA1;Product;00045;001234567;0,00\nA2;Missing price;009;;\n")
        rows, issues = import_products(source, mapping())
        self.assertFalse(issues)
        self.assertEqual(rows[0]["sale_price"], {"amount": "0.00", "currency": "EUR"})
        self.assertEqual(rows[0]["barcode"], "001234567")
        self.assertEqual(rows[0]["sku"], "00045")
        self.assertNotIn("sale_price", rows[1])
        self.assertEqual(rows[0]["source"]["provider"], "csv:catalog-demo")

    def test_stable_ids_scoped_by_store_and_namespace(self):
        source = self.csv("ref;label;sku;barcode;price\n01;Demo;;;12,50\n")
        a, _ = import_products(source, mapping())
        a_repeat, _ = import_products(source, mapping())
        other_store, _ = import_products(source, mapping(store_id="other"))
        other_ns, _ = import_products(source, mapping(source_namespace="different"))
        self.assertEqual(a[0]["id"], a_repeat[0]["id"])
        self.assertNotEqual(a[0]["id"], other_store[0]["id"])
        self.assertNotEqual(a[0]["id"], other_ns[0]["id"])

    def test_invalid_rows_return_only_codes_no_source_values(self):
        source = self.csv("ref;label;sku;barcode;price\nA1;good;;;4,50\nA1;duplicate;;;9,99\nB2;secret name;;;1.50\nC3;;;;\nD4;wrong price;;;20,00;extra\n")
        rows, issues = import_products(source, mapping())
        self.assertEqual(len(rows), 1)
        self.assertEqual([x.code for x in issues], [
            "duplicate_external_id", "invalid_price", "missing_required", "wrong_column_count"
        ])
        self.assertNotIn("secret name", repr(issues))

    def test_currency_can_come_from_a_column(self):
        base = mapping()
        del base["currency"]
        base["columns"]["currency"] = "ccy"
        source = self.csv("ref;label;sku;barcode;price;ccy\n001;hi;;;10,50;THB\n002;unknown;;;;\n003;broken;;;2,00;\n")
        rows, issues = import_products(source, base)
        self.assertEqual(rows[0]["sale_price"]["currency"], "THB")
        self.assertNotIn("sale_price", rows[1])
        self.assertEqual(issues[0].code, "invalid_currency")

    def test_mapping_rejects_ambiguous_or_unsafe_configuration(self):
        for broken in (
            mapping(columns={"external_id": "ref"}),
            mapping(columns={"external_id": "id", "name": "id"}),
            mapping(currency="euros"),
            mapping(unexpected=True),
            mapping(delimiter="\n"),
            mapping(version=2),
        ):
            with self.subTest(broken=broken), self.assertRaises(MappingError):
                validate_mapping(broken)

    def test_missing_header_and_duplicate_header_fails_before_import(self):
        for source in (
            "ref;label;sku;price\n1;name;;1,00\n",
            "ref;label;sku;barcode;price;ref\n1;name;;;1,00;1\n",
        ):
            with self.assertRaises(MappingError):
                import_products(self.csv(source), mapping())

    def test_hard_max_rows(self):
        with self.assertRaises(MappingError):
            import_products(self.csv("ref;label;sku;barcode;price\n1;one;;;1,00\n2;two;;;2,00\n"), mapping(), max_rows=1)

    def test_cli_rejects_invalid_file_without_overwriting(self):
        original = self.directory / "existing.jsonl"
        original.write_text("ORIGINAL", encoding="utf-8")
        source = self.csv("ref;label;sku;barcode;price\nA;good;;;1,00\nB;bad;;;secret\n")
        config = self.directory / "mapping.json"
        config.write_text(json.dumps(mapping()), encoding="utf-8")
        args = [sys.executable, str(SCRIPT), "--input", str(source), "--mapping", str(config), "--output", str(original)]
        strict = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(strict.returncode, 1, strict.stderr)
        self.assertEqual(original.read_text(), "ORIGINAL")
        self.assertNotIn("secret", strict.stderr)
        partial = subprocess.run(args + ["--allow-partial", "--overwrite"], cwd=ROOT, capture_output=True, text=True, check=False)
        self.assertEqual(partial.returncode, 0, partial.stderr)
        result = [json.loads(x) for x in original.read_text().splitlines()]
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "good")

    def test_cli_prevents_input_output_collision(self):
        source = self.csv("ref;label;sku;barcode;price\nA;good;;;1,00\n")
        config = self.directory / "mapping.json"
        config.write_text(json.dumps(mapping()), encoding="utf-8")
        result = subprocess.run([sys.executable, str(SCRIPT), "--input", str(source), "--mapping", str(config), "--output", str(source)], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertTrue(source.read_text(encoding="utf-8-sig").startswith("ref;"))


if __name__ == "__main__":
    unittest.main()
