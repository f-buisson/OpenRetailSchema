"""Regression tests use only synthetic, non-customer records."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate.py"
SAMPLES = ROOT / "examples"


class SchemaValidationTests(unittest.TestCase):
    def run_validator(self, relative: str):
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(SAMPLES / relative)],
            capture_output=True, text=True, check=False,
        )

    def test_valid_sale(self):
        self.assertEqual(self.run_validator("valid_sale.json").returncode, 0)

    def test_valid_product(self):
        self.assertEqual(self.run_validator("valid_product.json").returncode, 0)

    def test_valid_activity_metric(self):
        self.assertEqual(self.run_validator("valid_activity_metric.json").returncode, 0)

    def test_valid_refund_with_positive_source_quantity(self):
        self.assertEqual(self.run_validator("valid_refund.json").returncode, 0)

    def test_absent_product_price_is_distinct_from_reported_price(self):
        absent_price = json.loads((SAMPLES / "valid_product_missing_price.json").read_text(encoding="utf-8"))
        reported_price = json.loads((SAMPLES / "valid_product.json").read_text(encoding="utf-8"))

        self.assertEqual(self.run_validator("valid_product_missing_price.json").returncode, 0)
        self.assertEqual(self.run_validator("valid_product.json").returncode, 0)
        self.assertNotIn("sale_price", absent_price)
        self.assertEqual(reported_price["sale_price"], {"amount": "2.49", "currency": "EUR"})

    def test_absent_tax_is_distinct_from_explicit_zero_tax(self):
        absent_tax = json.loads((SAMPLES / "valid_sale.json").read_text(encoding="utf-8"))
        zero_tax = json.loads((SAMPLES / "valid_sale_zero_tax.json").read_text(encoding="utf-8"))

        self.assertEqual(self.run_validator("valid_sale.json").returncode, 0)
        self.assertEqual(self.run_validator("valid_sale_zero_tax.json").returncode, 0)
        self.assertNotIn("tax_total", absent_tax)
        self.assertEqual(zero_tax["tax_total"], {"amount": "0", "currency": "EUR"})

    def test_mixed_sale_currencies_are_rejected(self):
        result = self.run_validator("invalid_sale_mixed_currency.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("all monetary values in a sale must use one currency", result.stderr)

    def test_invalid_currency_code_shape_is_rejected(self):
        fixture = json.loads((SAMPLES / "invalid_product_currency_code.json").read_text(encoding="utf-8"))
        result = self.run_validator("invalid_product_currency_code.json")
        self.assertEqual(fixture["sale_price"]["currency"], "eur")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL", result.stderr)

    def test_dst_fallback_interval_is_ordered_by_absolute_instant(self):
        result = self.run_validator("valid_activity_dst_fallback.json")
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reversed_activity_interval_is_rejected(self):
        result = self.run_validator("invalid_activity_reversed.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("interval_end: must represent an instant after interval_start", result.stderr)

    def test_local_event_time_without_offset_is_rejected(self):
        result = self.run_validator("invalid_sale_local_time.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("date-time", result.stderr)

    def test_invalid_floating_point_money(self):
        result = self.run_validator("invalid_sale_float.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL", result.stderr)

    def test_missing_file_returns_failure(self):
        self.assertEqual(self.run_validator("missing.json").returncode, 1)

    def test_multiple_files_are_all_validated(self):
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(SAMPLES / "missing.json"),
             str(SAMPLES / "invalid_sale_float.json"), str(SAMPLES / "valid_product.json")],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing.json", result.stderr)
        self.assertIn("invalid_sale_float.json", result.stderr)
        self.assertIn("PASS", result.stdout)
        self.assertIn("valid_product.json", result.stdout)


if __name__ == "__main__":
    unittest.main()
