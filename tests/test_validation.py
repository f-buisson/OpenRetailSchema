"""Regression tests use only synthetic, non-customer records."""
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

    def test_invalid_floating_point_money(self):
        result = self.run_validator("invalid_sale_float.json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL", result.stderr)

    def test_missing_file_returns_failure(self):
        self.assertEqual(self.run_validator("missing.json").returncode, 1)


if __name__ == "__main__":
    unittest.main()
