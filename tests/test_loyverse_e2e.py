# SPDX-License-Identifier: Apache-2.0
"""Synthetic end-to-end Loyverse reads; never require a real account or token."""
from decimal import Decimal
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from connectors.loyverse import LoyverseClient, LoyverseError, canonical_product, canonical_sale

ROOT = Path(__file__).resolve().parents[1]


class SyntheticLoyverse:
    def __init__(self, *, fail_second_receipt_page=False):
        self.calls = []
        self.fail_second_receipt_page = fail_second_receipt_page

    def __call__(self, path, token):
        if token != "synthetic-token":
            raise AssertionError("unexpected token")
        self.calls.append(path)
        parsed = urlparse(path)
        query = parse_qs(parsed.query)
        cursor = query.get("cursor", [None])[0]
        if parsed.path == "/v1.0/merchant":
            return {"currency": {"code": "EUR"}}
        if parsed.path == "/v1.0/variants":
            if cursor is None:
                return {"variants": [{"id": "v1", "name": "Tea", "price": Decimal("2.50"), "updated_at": "2026-10-05T10:00:00Z"}], "cursor": "variants-2"}
            return {"variants": [{"id": "v2", "name": "Coffee", "price": None, "updated_at": "2026-10-05T11:00:00+00:00"}], "cursor": None}
        if parsed.path == "/v1.0/receipts":
            if cursor is None:
                return {"receipts": [{"receipt_number": "r1", "receipt_type": "SALE", "receipt_date": "2026-10-05T10:15:00Z", "store_id": "s1", "updated_at": "2026-10-05T10:16:00Z", "line_items": [{"id": "l1", "variant_id": "v1", "quantity": 1, "gross_total_money": Decimal("2.50")}]}], "cursor": "receipts-2"}
            if self.fail_second_receipt_page:
                raise LoyverseError("connection_failure")
            return {"receipts": [{"receipt_number": "r2", "receipt_type": "REFUND", "receipt_date": "2026-10-05T11:15:00Z", "store_id": "s1", "updated_at": "2026-10-05T11:16:00Z", "total_tax": None, "line_items": [{"id": "l2", "variant_id": "v2", "quantity": 1}]}], "cursor": None}
        raise AssertionError("unexpected path: " + path)


class LoyverseEndToEndTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with (ROOT / "schemas" / "v0.1" / "record.schema.json").open(encoding="utf-8") as stream:
            cls.validator = Draft202012Validator(json.load(stream), format_checker=FormatChecker())

    def test_paginated_products_and_receipts_map_to_schema_valid_records(self):
        transport = SyntheticLoyverse()
        client = LoyverseClient("synthetic-token", transport=transport)
        merchant = client.merchant()
        products, product_checkpoint = client.read_incremental("variants", transform=lambda row: canonical_product(row, merchant), limit=1)
        sales, sale_checkpoint = client.read_incremental("receipts", transform=lambda row: canonical_sale(row, merchant), limit=1)

        self.assertEqual([record["id"] for record in products], ["loyverse:variant:v1", "loyverse:variant:v2"])
        self.assertEqual([record["sale_kind"] for record in sales], ["sale", "refund"])
        self.assertEqual(product_checkpoint, "2026-10-05T11:00:00+00:00")
        self.assertEqual(sale_checkpoint, "2026-10-05T11:16:00Z")
        self.assertNotIn("sale_price", products[1], "null price must stay unknown, never zero")
        self.assertNotIn("gross_total", sales[1]["lines"][0], "missing line money must stay unknown, never zero")
        self.assertNotIn("tax_total", sales[1], "null tax must stay unknown, never zero")
        for record in products + sales:
            self.assertEqual(list(self.validator.iter_errors(record)), [])

        variant_calls = [path for path in transport.calls if "/variants?" in path]
        receipt_calls = [path for path in transport.calls if "/receipts?" in path]
        self.assertEqual(len(variant_calls), 2)
        self.assertEqual(len(receipt_calls), 2)
        self.assertIn("cursor=variants-2", variant_calls[1])
        self.assertIn("cursor=receipts-2", receipt_calls[1])

    def test_resume_uses_source_checkpoint_not_previous_pagination_cursor(self):
        transport = SyntheticLoyverse()
        client = LoyverseClient("synthetic-token", transport=transport)
        rows, checkpoint = client.read_incremental("variants", checkpoint="2026-10-05T09:00:00Z", limit=1)
        self.assertEqual(len(rows), 2)
        self.assertEqual(checkpoint, "2026-10-05T11:00:00+00:00")
        first_call = next(path for path in transport.calls if "/variants?" in path)
        self.assertIn("updated_at_min=2026-10-05T09%3A00%3A00Z", first_call)
        self.assertNotIn("cursor=", first_call)

    def test_failed_traversal_never_returns_a_partial_checkpoint(self):
        transport = SyntheticLoyverse(fail_second_receipt_page=True)
        client = LoyverseClient("synthetic-token", transport=transport, max_attempts=1)
        with self.assertRaises(LoyverseError) as ctx:
            client.read_incremental("receipts", checkpoint="2026-10-05T09:00:00Z", limit=1)
        self.assertEqual(ctx.exception.code, "connection_failure")


if __name__ == "__main__":
    unittest.main()
