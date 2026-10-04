# SPDX-License-Identifier: Apache-2.0
"""Offline, fabricated Loyverse transport tests. Never require a real token."""
from decimal import Decimal
import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator, FormatChecker

from connectors.loyverse import (
    LoyverseClient,
    LoyverseError,
    canonical_money,
    canonical_product,
    merchant_currency,
    source_decimal,
    source_external_id,
)


ROOT = Path(__file__).resolve().parents[1]


class LoyverseTests(unittest.TestCase):
    def test_token_validation(self):
        for token in ("", "bad\nvalue", "bad\rvalue"):
            with self.assertRaises(ValueError):
                LoyverseClient(token)

    def test_cursor_pagination_and_limit(self):
        calls = []

        def transport(path, token):
            self.assertEqual(token, "synthetic-token")
            calls.append(path)
            if "cursor=" in path:
                return {"items": [{"id": "item_b"}], "cursor": None}
            return {"items": [{"id": "item_a"}], "cursor": "next-cursor"}

        client = LoyverseClient("synthetic-token", transport=transport)
        rows = list(client.iter_collection("items", limit=2))
        self.assertEqual([r["id"] for r in rows], ["item_a", "item_b"])
        self.assertEqual(len(calls), 2)
        self.assertIn("limit=2", calls[0])
        self.assertIn("cursor=next-cursor", calls[1])

    def test_repeated_cursor_is_rejected(self):
        def transport(path, token):
            return {"receipts": [], "cursor": "stuck"}

        with self.assertRaises(LoyverseError) as ctx:
            list(LoyverseClient("synthetic-token", transport=transport).iter_collection("receipts"))
        self.assertEqual(ctx.exception.code, "invalid_pagination_cursor")

    def test_unexpected_payload_fails_closed(self):
        with self.assertRaises(LoyverseError):
            list(LoyverseClient("synthetic-token", transport=lambda path, token: {"items": None}).iter_collection("items"))

    def test_out_of_scope_resource_is_rejected(self):
        with self.assertRaises(ValueError):
            list(LoyverseClient("synthetic-token", transport=lambda path, token: {}).iter_collection("prices_write"))

    def test_page_limit_fails_explicitly(self):
        with self.assertRaises(LoyverseError) as ctx:
            list(LoyverseClient("synthetic-token", transport=lambda path, token: {"items": [], "cursor": "next"}).iter_collection("items", max_pages=1))
        self.assertEqual(ctx.exception.code, "page_limit_reached")

    def test_merchant_currency_preserves_unknown(self):
        self.assertEqual(merchant_currency({"currency": {"code": "THB", "decimal_places": 2}}), "THB")
        self.assertEqual(merchant_currency({"currency": "EUR"}), "EUR")
        self.assertIsNone(merchant_currency({"currency": None}))
        self.assertIsNone(merchant_currency({"currency": {"code": "BAHT-THAI"}}))

    def test_source_decimal_keeps_unknown_distinct_from_zero(self):
        for field in ("price", "in_stock"):
            self.assertIsNone(source_decimal({}, field))
            self.assertIsNone(source_decimal({field: None}, field))
            self.assertEqual(source_decimal({field: 0}, field), Decimal("0"))
            self.assertEqual(source_decimal({field: Decimal("0.000")}, field), Decimal("0.000"))

    def test_source_decimal_preserves_precision(self):
        value = Decimal("1234567890.12345678901234567890")
        self.assertEqual(source_decimal({"price": value}, "price"), value)
        self.assertEqual(source_decimal({"in_stock": -7}, "in_stock"), Decimal("-7"))

    def test_source_decimal_fails_closed_for_unsupported_values(self):
        unsupported = (
            True, False, float("nan"), float("inf"), 1.25, "12.50",
            "not-a-number", Decimal("NaN"), Decimal("Infinity"), [], {},
        )
        for value in unsupported:
            with self.subTest(value=value):
                self.assertIsNone(source_decimal({"price": value}, "price"))

    def test_source_external_id_preserves_opaque_string(self):
        for value in ("item_123", "  meaningful-id  ", "0"):
            with self.subTest(value=value):
                self.assertEqual(source_external_id({"id": value}), value)

    def test_source_external_id_fails_closed_without_valid_string(self):
        rejected = (None, "", "   ", True, False, 0, 42, 1.5, [], {}, ["id"])
        self.assertIsNone(source_external_id({}))
        self.assertIsNone(source_external_id(None))
        for value in rejected:
            with self.subTest(value=value):
                self.assertIsNone(source_external_id({"id": value}))

    def test_canonical_money_serializes_finite_values_exactly(self):
        merchant = {"currency": {"code": "EUR"}}
        cases = (
            (0, "0"), (Decimal("0.000"), "0.000"), (-9, "-9"),
            (Decimal("-9.90"), "-9.90"),
            (Decimal("1234567890.12345678901234567890"), "1234567890.12345678901234567890"),
            (Decimal("1E+3"), "1000"), (Decimal("1E-7"), "0.0000001"),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                self.assertEqual(canonical_money({"price": value}, "price", merchant), {"amount": expected, "currency": "EUR"})

    def test_canonical_money_preserves_unknown_amount(self):
        merchant = {"currency": "EUR"}
        for record in ({}, {"price": None}, {"price": "0"}, {"price": 1.5}, {"price": Decimal("NaN")}):
            with self.subTest(record=record):
                self.assertIsNone(canonical_money(record, "price", merchant))

    def test_canonical_money_requires_valid_merchant_currency(self):
        record = {"price": Decimal("2.49")}
        for merchant in ({}, {"currency": None}, {"currency": "eur"}, {"currency": "EURO"}, {"currency": {"code": "usd"}}):
            with self.subTest(merchant=merchant):
                self.assertIsNone(canonical_money(record, "price", merchant))

    def test_canonical_product_is_schema_valid_and_deterministic(self):
        variant = {"id": "variant_opaque", "name": "Synthetic tea", "sku": "TEA-1", "barcode": "000123", "price": Decimal("2.50")}
        merchant = {"currency": {"code": "EUR"}}
        first = canonical_product(variant, merchant)
        second = canonical_product(dict(variant), merchant)
        self.assertEqual(first, second)
        self.assertEqual(first["id"], "loyverse:variant:variant_opaque")
        self.assertEqual(first["source"], {"provider": "loyverse", "external_id": "variant_opaque"})
        self.assertEqual(first["sale_price"], {"amount": "2.50", "currency": "EUR"})
        with (ROOT / "schemas" / "v0.1" / "record.schema.json").open(encoding="utf-8") as stream:
            schema = json.load(stream)
        errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(first))
        self.assertEqual(errors, [])

    def test_canonical_product_keeps_missing_price_distinct_from_zero(self):
        merchant = {"currency": "EUR"}
        absent = canonical_product({"id": "a", "name": "Absent"}, merchant)
        null = canonical_product({"id": "n", "name": "Null", "price": None}, merchant)
        zero = canonical_product({"id": "z", "name": "Zero", "price": 0}, merchant)
        unsupported = canonical_product({"id": "s", "name": "String", "price": "0"}, merchant)
        self.assertNotIn("sale_price", absent)
        self.assertNotIn("sale_price", null)
        self.assertNotIn("sale_price", unsupported)
        self.assertEqual(zero["sale_price"], {"amount": "0", "currency": "EUR"})

    def test_canonical_product_rejects_invalid_required_fields(self):
        cases = (({}, "invalid_product_identity"), ({"id": "", "name": "X"}, "invalid_product_identity"), ({"id": "x"}, "invalid_product_name"), ({"id": "x", "name": "   "}, "invalid_product_name"))
        for variant, code in cases:
            with self.subTest(variant=variant):
                with self.assertRaises(LoyverseError) as ctx:
                    canonical_product(variant, {"currency": "EUR"})
                self.assertEqual(ctx.exception.code, code)

    def test_canonical_product_rejects_malformed_optional_fields(self):
        for field, value in (("sku", 123), ("sku", ""), ("barcode", False), ("barcode", "   ")):
            with self.subTest(field=field, value=value):
                with self.assertRaises(LoyverseError) as ctx:
                    canonical_product({"id": "x", "name": "Synthetic", field: value}, {"currency": "EUR"})
                self.assertEqual(ctx.exception.code, "invalid_product_" + field)

    def test_merchant_raw_response(self):
        raw = {"id": "synthetic", "currency": {"code": "THB", "decimal_places": 2}}
        self.assertEqual(LoyverseClient("synthetic-token", transport=lambda path, token: raw).merchant(), raw)

    def test_http_error_codes_do_not_expose_credentials(self):
        from connectors.loyverse import _http_error
        self.assertEqual(_http_error(402).code, "plan_restricted_history")
        self.assertEqual(_http_error(429).code, "rate_limited")
        self.assertEqual(_http_error(401).code, "unauthorized")
        self.assertNotIn("synthetic-token", str(_http_error(402)))


if __name__ == "__main__":
    unittest.main()
