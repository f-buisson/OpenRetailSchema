# SPDX-License-Identifier: Apache-2.0
import unittest

from connectors.square import SquareConnector, SquareResponseError


class SquarePaginationSafetyTests(unittest.TestCase):
    def test_repeated_get_cursor_fails_closed_before_the_page_budget(self):
        calls = []

        def transport(method, path, request):
            calls.append((method, path, request))
            return {"objects": [], "cursor": "stuck-cursor"}

        connector = SquareConnector(transport)
        with self.assertRaisesRegex(SquareResponseError, "^square_cursor_repeated$"):
            connector.read("products.read", max_pages=50)

        # The budget is deliberately far larger than the traversal: the second
        # page already repeats, so 48 pages are never requested.
        self.assertEqual(len(calls), 2)
        self.assertNotIn("cursor", calls[0][2]["params"])
        self.assertEqual(calls[1][2]["params"]["cursor"], "stuck-cursor")

    def test_repeated_post_cursor_fails_closed_before_the_page_budget(self):
        calls = []

        def transport(method, path, request):
            calls.append((method, path, request))
            return {"counts": [], "cursor": "stuck-cursor"}

        connector = SquareConnector(transport)
        with self.assertRaisesRegex(SquareResponseError, "^square_cursor_repeated$"):
            connector.read("inventory.read", max_pages=50)

        self.assertEqual(len(calls), 2)
        self.assertNotIn("cursor", calls[0][2]["json"])
        self.assertEqual(calls[1][2]["json"]["cursor"], "stuck-cursor")

    def test_page_budget_still_stops_a_traversal_whose_cursors_all_differ(self):
        calls = []

        def transport(method, path, request):
            calls.append((method, path, request))
            return {"objects": [], "cursor": "page-" + str(len(calls))}

        connector = SquareConnector(transport)
        with self.assertRaisesRegex(SquareResponseError, "^square_pagination_limit_exceeded$"):
            connector.read("products.read", max_pages=3)

        # Without this, cycle detection would hide the budget: every repeating
        # traversal now dies earlier, and nothing else would notice the budget
        # breaking.
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[1][2]["params"]["cursor"], "page-1")
        self.assertEqual(calls[2][2]["params"]["cursor"], "page-2")

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
