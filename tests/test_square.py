# SPDX-License-Identifier: Apache-2.0
import unittest

from connectors.square import SquareConnector, SquareResponseError, canonical_square_products, canonical_square_sales
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

    def test_sales_with_no_locations_makes_no_order_search(self):
        connector, calls = self.connector([{"locations": []}])
        self.assertEqual(connector.read("sales.read"), [])
        self.assertEqual([path for _, path, _ in calls], ["/v2/locations"])

    def test_sales_rejects_a_locations_page_missing_the_property(self):
        cases = (
            ("first page", [{}], 1),
            ("page carrying only a cursor", [{"cursor": "next"}], 1),
            ("subsequent page", [{"locations": [{"id": "location-1"}], "cursor": "next"}, {}], 2),
            ("empty first page then an incomplete one", [{"locations": [], "cursor": "next"}, {}], 2),
        )
        for label, responses, location_calls in cases:
            with self.subTest(case=label):
                connector, calls = self.connector(responses)
                with self.assertRaises(SquareResponseError) as raised:
                    connector.read("sales.read")
                self.assertEqual(str(raised.exception), "square_locations_missing")
                # A location set that could not be learned must never become an
                # order search: a partial set would report fewer sales as success.
                self.assertEqual([path for _, path, _ in calls], ["/v2/locations"] * location_calls)

    def test_sales_keeps_an_empty_locations_page_distinct_from_a_missing_one(self):
        connector, calls = self.connector([
            {"locations": [], "cursor": "next"},
            {"locations": [{"id": "location-1"}]},
            {"orders": [{"id": "order-a"}]},
        ])
        self.assertEqual(connector.read("sales.read"), [{"id": "order-a"}])
        self.assertEqual(
            [path for _, path, _ in calls],
            ["/v2/locations", "/v2/locations", "/v2/orders/search"],
        )

    def test_missing_locations_error_carries_no_payload_data(self):
        connector, _ = self.connector([{"merchant_id": "merchant-private", "detail": "payload-detail"}])
        with self.assertRaises(SquareResponseError) as raised:
            connector.read("sales.read")
        self.assertEqual(str(raised.exception), "square_locations_missing")
        self.assertNotIn("merchant-private", str(raised.exception))
        self.assertNotIn("payload-detail", str(raised.exception))

    def test_locations_requirement_does_not_leak_into_other_reads(self):
        for operation in ("products.read", "inventory.read"):
            with self.subTest(operation=operation):
                connector, _ = self.connector([{}])
                raised = None
                try:
                    connector.read(operation)
                except SquareResponseError as error:
                    raised = str(error)
                # Only the locations traversal was made to require its result key.
                # What a catalog or inventory payload missing its own result key
                # ought to do is a separate question, still open; it must never be
                # answered with a locations error code.
                self.assertNotEqual(raised, "square_locations_missing")

    def test_sales_rejects_invalid_location_entries_before_order_search(self):
        invalid_cases = (
            (None, "square_location_must_be_object"),
            ("location-sensitive", "square_location_must_be_object"),
            ({}, "square_location_id_invalid"),
            ({"id": None}, "square_location_id_invalid"),
            ({"id": ""}, "square_location_id_invalid"),
            ({"id": "   "}, "square_location_id_invalid"),
            ({"id": 3}, "square_location_id_invalid"),
            ({"id": 0}, "square_location_id_invalid"),
            ({"id": False}, "square_location_id_invalid"),
            ({"id": {}}, "square_location_id_invalid"),
            ({"id": True}, "square_location_id_invalid"),
            ({"id": []}, "square_location_id_invalid"),
        )
        for bad_entry, error_code in invalid_cases:
            with self.subTest(entry=type(bad_entry).__name__, code=error_code):
                connector, calls = self.connector([{
                    "locations": [{"id": "location-valid"}, bad_entry],
                }])
                with self.assertRaises(SquareResponseError) as raised:
                    connector.read("sales.read")
                self.assertEqual(str(raised.exception), error_code)
                self.assertEqual([path for _, path, _ in calls], ["/v2/locations"])
                self.assertNotIn("location-sensitive", str(raised.exception))

    def test_sales_rejects_duplicate_location_ids_across_pages(self):
        connector, calls = self.connector([
            {"locations": [{"id": "location-1"}], "cursor": "next"},
            {"locations": [{"id": "location-2"}, {"id": "location-1"}]},
        ])
        with self.assertRaises(SquareResponseError) as raised:
            connector.read("sales.read")
        self.assertEqual(str(raised.exception), "square_location_id_repeated")
        self.assertEqual([path for _, path, _ in calls], ["/v2/locations", "/v2/locations"])

    def test_sales_rejects_duplicate_location_ids_within_page(self):
        connector, calls = self.connector([{
            "locations": [{"id": "location-1"}, {"id": "location-1"}],
        }])
        with self.assertRaises(SquareResponseError) as raised:
            connector.read("sales.read")
        self.assertEqual(str(raised.exception), "square_location_id_repeated")
        self.assertEqual([path for _, path, _ in calls], ["/v2/locations"])

    def test_sales_valid_locations_preserve_order_and_batch_boundaries(self):
        ids = [f"location-{index}" for index in range(11)]
        connector, calls = self.connector([
            {"locations": [{"id": item} for item in ids]},
            {"orders": [{"id": "order-a"}]},
            {"orders": [{"id": "order-b"}]},
        ])
        self.assertEqual(connector.read("sales.read"), [{"id": "order-a"}, {"id": "order-b"}])
        batches = [request["json"]["location_ids"] for _, path, request in calls if path == "/v2/orders/search"]
        self.assertEqual(batches, [ids[:10], ids[10:]])

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

    def test_repeated_cursor_fails_closed_on_get_and_post(self):
        for operation, result_key, request_key in (
            ("products.read", "objects", "params"),
            ("inventory.read", "counts", "json"),
        ):
            with self.subTest(operation=operation):
                connector, calls = self.connector([
                    {result_key: [{"id": "first"}], "cursor": "same"},
                    {result_key: [{"id": "second"}], "cursor": "same"},
                ])
                with self.assertRaisesRegex(SquareResponseError, "^square_cursor_repeated$") as raised:
                    connector.read(operation)
                self.assertEqual(len(calls), 2)
                self.assertEqual(calls[1][2][request_key]["cursor"], "same")
                self.assertNotIn("same", str(raised.exception))

    def test_nonadjacent_cursor_cycle_fails_closed_on_get_and_post(self):
        for operation, result_key in (("stores.read", "locations"), ("inventory.read", "counts")):
            with self.subTest(operation=operation):
                connector, calls = self.connector([
                    {result_key: [], "cursor": "first"},
                    {result_key: [], "cursor": "second"},
                    {result_key: [], "cursor": "first"},
                ])
                with self.assertRaisesRegex(SquareResponseError, "^square_cursor_repeated$"):
                    connector.read(operation)
                self.assertEqual(len(calls), 3)

    def test_malformed_cursors_fail_closed_before_extra_requests(self):
        for operation, result_key in (("products.read", "objects"), ("inventory.read", "counts")):
            for invalid in (0, False, True, [], {}, 1.5):
                with self.subTest(operation=operation, invalid=repr(invalid)):
                    connector, calls = self.connector([{result_key: [], "cursor": invalid}])
                    with self.assertRaisesRegex(SquareResponseError, "^square_cursor_must_be_string$"):
                        connector.read(operation)
                    self.assertEqual(len(calls), 1)

    def test_distinct_cursors_and_empty_terminal_cursor_succeed(self):
        for operation, result_key, request_key in (
            ("products.read", "objects", "params"),
            ("inventory.read", "counts", "json"),
        ):
            with self.subTest(operation=operation):
                connector, calls = self.connector([
                    {result_key: [{"id": "one"}], "cursor": "next-1"},
                    {result_key: [{"id": "two"}], "cursor": "next-2"},
                    {result_key: [{"id": "three"}], "cursor": ""},
                ])
                self.assertEqual(connector.read(operation), [
                    {"id": "one"}, {"id": "two"}, {"id": "three"},
                ])
                self.assertEqual(len(calls), 3)
                self.assertEqual(calls[1][2][request_key]["cursor"], "next-1")
                self.assertEqual(calls[2][2][request_key]["cursor"], "next-2")

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
        self.assertEqual(records[0]["sale_price"], {"amount": "5.00", "currency": "USD"})
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

    def test_product_money_preserves_zero_and_supports_zero_decimal_currency(self):
        records = canonical_square_products([
            {"type": "ITEM", "id": "i", "item_data": {"name": "Item"}},
            {"type": "ITEM_VARIATION", "id": "usd", "item_variation_data": {"item_id": "i", "pricing_type": "FIXED_PRICING", "price_money": {"amount": 0, "currency": "USD"}}},
            {"type": "ITEM_VARIATION", "id": "jpy", "item_variation_data": {"item_id": "i", "pricing_type": "FIXED_PRICING", "price_money": {"amount": 500, "currency": "JPY"}}},
        ])
        self.assertEqual(records[0]["sale_price"], {"amount": "0.00", "currency": "USD"})
        self.assertEqual(records[1]["sale_price"], {"amount": "500", "currency": "JPY"})

    def test_product_money_fails_closed_for_unproven_or_malformed_values(self):
        parent = {"type": "ITEM", "id": "i", "item_data": {"name": "Item"}}
        def variation(price_money, pricing_type="FIXED_PRICING"):
            return {"type": "ITEM_VARIATION", "id": "v", "item_variation_data": {"item_id": "i", "pricing_type": pricing_type, "price_money": price_money}}
        with self.assertRaisesRegex(SquareResponseError, "square_money_currency_unsupported"):
            canonical_square_products([parent, variation({"amount": 100, "currency": "XXX"})])
        with self.assertRaisesRegex(SquareResponseError, "square_money_amount_must_be_integer"):
            canonical_square_products([parent, variation({"amount": 1.5, "currency": "USD"})])
        with self.assertRaisesRegex(SquareResponseError, "square_variable_pricing_has_price"):
            canonical_square_products([parent, variation({"amount": 100, "currency": "USD"}, "VARIABLE_PRICING")])
        # Python bools are ints, so an amount check that only asked for int would
        # read True as one cent.
        with self.assertRaisesRegex(SquareResponseError, "square_money_amount_must_be_integer"):
            canonical_square_products([parent, variation({"amount": True, "currency": "USD"})])
        # A product sale price is a price. The canonical money pattern accepts a
        # sign, so a negative amount would validate and still mean nothing here.
        with self.assertRaisesRegex(SquareResponseError, "square_variation_price_negative"):
            canonical_square_products([parent, variation({"amount": -500, "currency": "USD"})])
        with self.assertRaisesRegex(SquareResponseError, "square_money_must_be_object"):
            canonical_square_products([parent, variation([100, "USD"])])
        with self.assertRaisesRegex(SquareResponseError, "square_pricing_type_unsupported"):
            canonical_square_products([parent, variation({"amount": 100, "currency": "USD"}, "TIERED_PRICING")])


    def test_completed_sale_normalization_preserves_only_proven_semantics(self):
        records = canonical_square_sales([
            {"id": "open-order", "state": "OPEN"},
            {
                "id": "order-1",
                "location_id": "location-1",
                "state": "COMPLETED",
                "closed_at": "2026-10-06T12:34:56Z",
                "total_money": {"amount": 1099, "currency": "EUR"},
                "line_items": [
                    {
                        "uid": "line-1",
                        "catalog_object_id": "variation-1",
                        "quantity": "2.500",
                        "gross_sales_money": {"amount": 1099, "currency": "EUR"},
                    }
                ],
            },
        ])
        self.assertEqual(records, [{
            "schema_version": "0.1.0",
            "entity_type": "sale",
            "id": "square:order:order-1",
            "source": {"provider": "square", "external_id": "order-1"},
            "store_id": "location-1",
            "occurred_at": "2026-10-06T12:34:56Z",
            "sale_kind": "sale",
            "lines": [{
                "id": "square:line:order-1:line-1",
                "source_product_id": "variation-1",
                "quantity": "2.500",
            }],
        }])
        self.assertNotIn("gross_total", records[0])
        self.assertNotIn("net_total", records[0])
        self.assertNotIn("tax_total", records[0])
        self.assertNotIn("gross_total", records[0]["lines"][0])

    def test_completed_sale_rejects_return_bearing_or_unmappable_orders(self):
        base = {
            "id": "order-1",
            "location_id": "location-1",
            "state": "COMPLETED",
            "closed_at": "2026-10-06T12:34:56+00:00",
            "line_items": [{"uid": "line-1", "catalog_object_id": "variation-1", "quantity": "1"}],
        }
        with self.assertRaisesRegex(SquareResponseError, "square_order_returns_not_normalized"):
            canonical_square_sales([{**base, "returns": [{"uid": "return-1"}]}])
        with self.assertRaisesRegex(SquareResponseError, "square_order_closed_at_required"):
            canonical_square_sales([{**base, "closed_at": "2026-10-06T12:34:56"}])
        with self.assertRaisesRegex(SquareResponseError, "square_order_line_product_required"):
            canonical_square_sales([{**base, "line_items": [{"uid": "line-1", "quantity": "1"}]}])
        with self.assertRaisesRegex(SquareResponseError, "square_order_line_quantity_required"):
            canonical_square_sales([{**base, "line_items": [{"uid": "line-1", "catalog_object_id": "variation-1", "quantity": "NaN"}]}])


if __name__ == "__main__":
    unittest.main()
