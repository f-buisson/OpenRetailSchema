# SPDX-License-Identifier: Apache-2.0
"""Synthetic receipt normalization tests; no real Loyverse payloads or credentials."""
from decimal import Decimal
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from connectors.loyverse import LoyverseError, canonical_sale


ROOT = Path(__file__).resolve().parents[1]


def fabricated_receipt(**overrides):
    receipt = {
        "receipt_number": "synthetic-receipt-1",
        "receipt_type": "SALE",
        "receipt_date": "2026-10-04T01:02:03Z",
        "store_id": "synthetic-store-1",
        "total_money": Decimal("4.50"),
        "total_tax": Decimal("0.50"),
        "line_items": [
            {
                "id": "synthetic-line-1",
                "variant_id": "synthetic-variant-1",
                "quantity": Decimal("2"),
                "gross_total_money": Decimal("5.00"),
            }
        ],
    }
    receipt.update(overrides)
    return receipt


class LoyverseSaleTests(unittest.TestCase):
    def setUp(self):
        self.merchant = {"currency": {"code": "EUR"}}

    def test_canonical_sale_is_schema_valid_and_deterministic(self):
        first = canonical_sale(fabricated_receipt(), self.merchant)
        second = canonical_sale(fabricated_receipt(), self.merchant)
        self.assertEqual(first, second)
        self.assertEqual(first["id"], "loyverse:receipt:synthetic-receipt-1")
        self.assertEqual(first["source"], {"provider": "loyverse", "external_id": "synthetic-receipt-1"})
        self.assertEqual(first["store_id"], "synthetic-store-1")
        self.assertEqual(first["occurred_at"], "2026-10-04T01:02:03Z")
        self.assertEqual(first["sale_kind"], "sale")
        self.assertEqual(first["lines"][0]["source_product_id"], "synthetic-variant-1")
        self.assertEqual(first["lines"][0]["quantity"], "2")
        self.assertEqual(first["lines"][0]["gross_total"], {"amount": "5.00", "currency": "EUR"})
        with (ROOT / "schemas" / "v0.1" / "record.schema.json").open(encoding="utf-8") as stream:
            schema = json.load(stream)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(first))
        self.assertEqual(errors, [])

    def test_refund_preserves_documented_positive_source_signs(self):
        receipt = fabricated_receipt(
            receipt_type="REFUND",
            total_money=Decimal("2.50"),
            line_items=[{
                "id": "refund-line",
                "variant_id": "synthetic-variant-1",
                "quantity": Decimal("1"),
                "gross_total_money": Decimal("2.50"),
            }],
        )
        record = canonical_sale(receipt, self.merchant)
        self.assertEqual(record["sale_kind"], "refund")
        self.assertEqual(record["lines"][0]["quantity"], "1")
        self.assertEqual(record["lines"][0]["gross_total"]["amount"], "2.50")

    def test_money_keeps_missing_distinct_from_zero_and_rejects_binary_float(self):
        missing = fabricated_receipt(line_items=[{
            "id": "missing-money", "variant_id": "v", "quantity": 1,
        }])
        zero = fabricated_receipt(line_items=[{
            "id": "zero-money", "variant_id": "v", "quantity": 1, "gross_total_money": 0,
        }])
        unsupported = fabricated_receipt(line_items=[{
            "id": "float-money", "variant_id": "v", "quantity": 1, "gross_total_money": 0.0,
        }])
        self.assertNotIn("gross_total", canonical_sale(missing, self.merchant)["lines"][0])
        self.assertEqual(canonical_sale(zero, self.merchant)["lines"][0]["gross_total"]["amount"], "0")
        self.assertNotIn("gross_total", canonical_sale(unsupported, self.merchant)["lines"][0])

    def test_required_identity_time_kind_and_line_fail_closed(self):
        cases = (
            ({"receipt_number": ""}, "invalid_sale_identity"),
            ({"store_id": None}, "invalid_sale_store"),
            ({"receipt_date": "2026-10-04T01:02:03"}, "invalid_sale_time"),
            ({"receipt_type": "UNKNOWN"}, "invalid_sale_kind"),
            ({"line_items": []}, "invalid_sale_lines"),
            ({"line_items": [{"id": "line", "quantity": 1}]}, "invalid_sale_line"),
            ({"line_items": [{"id": "line", "variant_id": "v", "quantity": True}]}, "invalid_sale_line"),
        )
        for overrides, expected in cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(LoyverseError) as ctx:
                    canonical_sale(fabricated_receipt(**overrides), self.merchant)
                self.assertEqual(ctx.exception.code, expected)


if __name__ == "__main__":
    unittest.main()
