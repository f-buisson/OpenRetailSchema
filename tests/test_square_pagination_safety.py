# SPDX-License-Identifier: Apache-2.0
import unittest

from connectors.square import SquareConnector, SquareResponseError


class SquarePaginationSafetyTests(unittest.TestCase):
    def test_repeated_get_cursor_stops_at_page_budget(self):
        calls = []

        def transport(method, path, request):
            calls.append((method, path, request))
            return {"objects": [], "cursor": "stuck-cursor"}

        connector = SquareConnector(transport)
        with self.assertRaisesRegex(SquareResponseError, "square_pagination_limit_exceeded"):
            connector.read("products.read", max_pages=2)

        self.assertEqual(len(calls), 2)
        self.assertNotIn("cursor", calls[0][2]["params"])
        self.assertEqual(calls[1][2]["params"]["cursor"], "stuck-cursor")

    def test_repeated_post_cursor_stops_at_page_budget(self):
        calls = []

        def transport(method, path, request):
            calls.append((method, path, request))
            return {"counts": [], "cursor": "stuck-cursor"}

        connector = SquareConnector(transport)
        with self.assertRaisesRegex(SquareResponseError, "square_pagination_limit_exceeded"):
            connector.read("inventory.read", max_pages=3)

        self.assertEqual(len(calls), 3)
        self.assertNotIn("cursor", calls[0][2]["json"])
        self.assertEqual(calls[1][2]["json"]["cursor"], "stuck-cursor")
        self.assertEqual(calls[2][2]["json"]["cursor"], "stuck-cursor")

    def test_page_budget_one_never_makes_an_extra_transport_call(self):
        calls = []

        def transport(method, path, request):
            calls.append((method, path, request))
            return {"objects": [{"id": "first-page"}], "cursor": "next"}

        connector = SquareConnector(transport)
        with self.assertRaisesRegex(SquareResponseError, "square_pagination_limit_exceeded"):
            connector.read("products.read", max_pages=1)

        self.assertEqual(len(calls), 1)


if __name__ == "__main__":
    unittest.main()
