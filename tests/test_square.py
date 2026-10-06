# SPDX-License-Identifier: Apache-2.0
import unittest

from connectors.square import SquareConnector, SquareResponseError, canonical_square_products
from tests.connector_conformance import exercise_read_connector


class SquareConnectorTests(unittest.TestCase):
    def connector(self, responses, **kwargs):
        calls = []
        queue = list(responses)

        def transport(method, path, request):
            calls.append((method, path, request))
            if not queue:
                raise AssertionError("unexpected_transport_call")
            return queue.pop(0)

        return SquareConnector(transport, **kwargs), calls

    def conformance_factory(self, operation):
        if operation is None:
            connector, calls = self.connector([])
            return connector, None, calls
        if operation == "products.read":
            expected = [{"id": "variation-1"}]
            connector, calls = self.connector([{"objects": expected}])
        elif operation == "stores.read":
            expected = [{"id": "location-1"}]
            connector, calls = self.connector([{"locations": expected}])
        elif operation == "sales.read":
            expected = [{"id": "order-1"}]
            connector, calls = self.connector([{"locations": [{"id": "location-1"}]}, {"orders": expected}])
        elif operation == "inventory.read":
            expected = [{"catalog_object_id": "variation-1", "quantity": "2"}]
            connector, calls = self.connector([{"counts": expected}])
        else:
            raise AssertionError("unknown_fixture_operation")
        return connector, expected, calls

    def test_reusable_connector_conformance(self):
        exercise_read_connector(self, self.conformance_factory)

    def test_catalog_pagination_preserves_cursor_and_type_filter(self):
        connector, calls = self.connector([{"objects": [{"id": "a"}], "cursor": "next-page"}, {"objects": [{"id": "b"}]}])
        self.assertEqual(connector.read("products.read"), [{"id": "a"}, {"id": "b"}])
        self.assertEqual(calls[0][2]["params"], {"types": "ITEM,ITEM_VARIATION"})
        self.assertEqual(calls[1][2]["params"]["cursor"], "next-page")

    def test_sales_chunks_locations_at_square_limit_of_ten(self):
        locations = [{"id": f"location-{index}"} for index in range(11)]
        connector, calls = self.connector([{"locations": locations}, {"orders": [{"id": "first"}]}, {"orders": [{"id": "second"}]}])
        self.assertEqual(connector.read("sales.read"), [{"id": "first"}, {"id": "second"}])
        order_calls = [call for call in calls if call[1] == "/v2/orders/search"]
        self.assertEqual(len(order_calls[0][2]["json"]["location_ids"]), 10)
        self.assertEqual(len(order_calls[1][2]["json"]["location_ids"]), 1)

    def test_rate_limit_retries_are_bounded_and_use_backoff(self):
        delays = []
        connector, calls = self.connector([{"errors": [{"code": "RATE_LIMITED"}]}, {"errors": [{"code": "RATE_LIMITED"}]}, {"locations": [{"id": "location-1"}]}], max_retries=2, sleeper=delays.append)
        self.assertEqual(connector.read("stores.read"), [{"id": "location-1"}])
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [1.0, 2.0])

    def test_rate_limit_exhaustion_fails_closed_without_extra_call(self):
        delays = []
        connector, calls = self.connector([{"errors": [{"code": "RATE_LIMITED"}]}, {"errors": [{"code": "RATE_LIMITED"}]}], max_retries=1, sleeper=delays.append)
        with self.assertRaisesRegex(SquareResponseError, "square_provider_error"):
            connector.read("stores.read")
        self.assertEqual(len(calls), 2)
        self.assertEqual(delays, [1.0])

    def test_non_rate_limit_provider_error_is_not_retried(self):
        connector, calls = self.connector([{"errors": [{"code": "UNAUTHORIZED", "detail": "secret-like detail"}]}], max_retries=2)
        with self.assertRaisesRegex(SquareResponseError, "square_provider_error") as raised:
            connector.read("stores.read")
        self.assertEqual(len(calls), 1)
        self.assertNotIn("secret-like detail", str(raised.exception))

    def test_invalid_retry_configuration_fails_before_transport(self):
        with self.assertRaisesRegex(ValueError, "max_retries_must_be_non_negative_integer"):
            SquareConnector(lambda *_args: {}, max_retries=-1)
        with self.assertRaisesRegex(ValueError, "max_retries_must_be_non_negative_integer"):
            SquareConnector(lambda *_args: {}, max_retries=True)

    def test_invalid_cursor_and_page_limit_fail_closed(self):
        connector, _ = self.connector([{"objects": [], "cursor": 123}])
        with self.assertRaisesRegex(SquareResponseError, "square_cursor_must_be_string"):
            connector.read("products.read")
        connector, _ = self.connector([])
        with self.assertRaisesRegex(ValueError, "max_pages_must_be_positive"):
            connector.read("products.read", max_pages=0)

    def test_product_normalization_preserves_identity_and_absence(self):
        records = canonical_square_products([
            {"type": "ITEM", "id": "item-1", "item_data": {"name": "Coffee"}},
            {"type": "ITEM_VARIATION", "id": "variation-1", "is_deleted": False,
             "item_variation_data": {"item_id": "item-1", "name": "Large", "sku": "COF-L",
                                     "upc": "123456789012", "pricing_type": "FIXED_PRICING",
                                     "price_money": {"amount": 500, "currency": "USD"}}},
            {"type": "ITEM_VARIATION", "id": "variation-2",
             "item_variation_data": {"item_id": "item-1", "name": "Variable", "pricing_type": "VARIABLE_PRICING"}},
        ])
        self.assertEqual(records[0]["id"], "square:variation:variation-1")
        self.assertEqual(records[0]["source"], {"provider": "square", "external_id": "variation-1"})
        self.assertEqual(records[0]["name"], "Coffee")
        self.assertEqual(records[0]["sku"], "COF-L")
        self.assertEqual(records[0]["barcode"], "123456789012")
        self.assertIs(records[0]["active"], True)
        self.assertNotIn("sale_price", records[0])
        self.assertNotIn("sale_price", records[1])
        self.assertNotIn("sku", records[1])
        self.assertNotIn("barcode", records[1])
        self.assertNotIn("active", records[1])

    def test_product_normalization_rejects_orphan_and_invalid_optional_values(self):
        with self.assertRaisesRegex(SquareResponseError, "square_variation_parent_missing"):
            canonical_square_products([{"type": "ITEM_VARIATION", "id": "v", "item_variation_data": {"item_id": "missing"}}])
        with self.assertRaisesRegex(SquareResponseError, "square_variation_sku_invalid"):
            canonical_square_products([
                {"type": "ITEM", "id": "i", "item_data": {"name": "Item"}},
                {"type": "ITEM_VARIATION", "id": "v", "item_variation_data": {"item_id": "i", "sku": ""}},
            ])


if __name__ == "__main__":
    unittest.main()
