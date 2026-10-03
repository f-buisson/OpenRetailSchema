# SPDX-License-Identifier: Apache-2.0
"""Offline, fabricated Loyverse transport tests. Never require a real token."""
import unittest

from connectors.loyverse import LoyverseClient, LoyverseError, merchant_currency


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

    def test_merchant_currency_accepts_only_explicit_supported_shapes(self):
        self.assertEqual(merchant_currency({"currency": "EUR"}), "EUR")
        self.assertEqual(
            merchant_currency({"currency": {"code": "THB", "decimal_places": 2}}),
            "THB",
        )

    def test_merchant_currency_preserves_missing_or_unsupported(self):
        unsupported = (
            {},
            {"currency": None},
            {"currency": ""},
            {"currency": "eur"},
            {"currency": "EU"},
            {"currency": "EURO"},
            {"currency": 978},
            {"currency": []},
            {"currency": {}},
            {"currency": {"code": None}},
            {"currency": {"code": "thb"}},
            {"currency": {"code": "BAHT-THAI"}},
            {"currency": {"code": 764}},
        )
        for merchant in unsupported:
            with self.subTest(merchant=merchant):
                self.assertIsNone(merchant_currency(merchant))
        self.assertIsNone(merchant_currency(None))
        self.assertIsNone(merchant_currency("not-a-merchant"))

    def test_merchant_currency_is_normalization_only(self):
        merchant = {
            "id": "synthetic-merchant",
            "currency": {"code": "USD", "decimal_places": 2},
            "name": "Fabricated Store",
        }
        self.assertEqual(merchant_currency(merchant), "USD")
        self.assertIsInstance(merchant_currency(merchant), str)
        self.assertNotIsInstance(merchant_currency(merchant), dict)

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
