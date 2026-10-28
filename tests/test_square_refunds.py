# SPDX-License-Identifier: Apache-2.0
import unittest

from connectors.square import SquareResponseError, canonical_square_refunds


class SquareRefundNormalizationTests(unittest.TestCase):
    def test_completed_refund_uses_payment_time_and_return_itemization(self):
        records = canonical_square_refunds(
            [{
                "id": "refund-order-1",
                "location_id": "location-1",
                "returns": [{
                    "source_order_id": "sale-order-1",
                    "return_line_items": [{
                        "uid": "return-line-1",
                        "source_line_item_uid": "sale-line-1",
                        "catalog_object_id": "variation-1",
                        "quantity": "1.500",
                        "total_money": {"amount": 750, "currency": "EUR"},
                    }],
                }],
            }],
            [{
                "id": "payment-refund-1",
                "order_id": "refund-order-1",
                "location_id": "location-1",
                "status": "COMPLETED",
                "created_at": "2026-10-06T16:30:00Z",
                "amount_money": {"amount": 750, "currency": "EUR"},
            }],
        )
        self.assertEqual(len(records), 1)
        record = records[0]
        self.assertEqual(record["id"], "square:refund:payment-refund-1")
        self.assertEqual(record["occurred_at"], "2026-10-06T16:30:00Z")
        self.assertEqual(record["sale_kind"], "refund")
        self.assertEqual(record["lines"][0]["source_product_id"], "variation-1")
        self.assertEqual(record["lines"][0]["quantity"], "1.500")
        self.assertEqual(record["lines"][0]["extensions"]["square:source_sale_line_id"], "square:line:sale-order-1:sale-line-1")
        self.assertNotIn("gross_total", record)
        self.assertNotIn("gross_total", record["lines"][0])

    def test_pending_refund_does_not_create_event(self):
        self.assertEqual(canonical_square_refunds([], [{
            "id": "pending", "status": "PENDING", "order_id": "refund-order-1"
        }]), [])

    def test_ambiguous_payment_allocation_fails_closed(self):
        order = {"id": "refund-order-1", "returns": [{"source_order_id": "sale-order-1", "return_line_items": []}]}
        refunds = [
            {"id": "r1", "order_id": "refund-order-1", "status": "COMPLETED", "created_at": "2026-10-06T16:00:00Z", "location_id": "l"},
            {"id": "r2", "order_id": "refund-order-1", "status": "COMPLETED", "created_at": "2026-10-06T16:01:00Z", "location_id": "l"},
        ]
        with self.assertRaisesRegex(SquareResponseError, "square_refund_payment_link_ambiguous"):
            canonical_square_refunds([order], refunds)

    def test_missing_item_link_and_naive_timestamp_fail_closed(self):
        base_order = {
            "id": "refund-order-1", "location_id": "location-1",
            "returns": [{"source_order_id": "sale-order-1", "return_line_items": [{
                "uid": "return-line-1", "catalog_object_id": "variation-1", "quantity": "1"
            }]}],
        }
        refund = {"id": "r1", "order_id": "refund-order-1", "status": "COMPLETED",
                  "created_at": "2026-10-06T16:00:00Z", "location_id": "location-1"}
        with self.assertRaisesRegex(SquareResponseError, "square_return_source_line_required"):
            canonical_square_refunds([base_order], [refund])
        refund["created_at"] = "2026-10-06T16:00:00"
        base_order["returns"][0]["return_line_items"][0]["source_line_item_uid"] = "sale-line-1"
        with self.assertRaisesRegex(SquareResponseError, "square_payment_refund_created_at_required"):
            canonical_square_refunds([base_order], [refund])


    def test_refund_created_at_rejects_non_rfc3339_forms(self):
        return_order = {
            "id": "refund-order-1", "location_id": "location-1",
            "returns": [{
                "source_order_id": "sale-order-1",
                "return_line_items": [{
                    "uid": "return-line-1", "source_line_item_uid": "sale-line-1",
                    "catalog_object_id": "variation-1", "quantity": "1",
                }],
            }],
        }
        refund = {
            "id": "refund-1", "order_id": "refund-order-1", "location_id": "location-1",
            "status": "COMPLETED", "created_at": "2026-10-06T16:30:00Z",
        }
        for timestamp in (
            "2026-10-06 16:30:00+00:00",
            "20261006T163000+00:00",
            "2026-10-06T16:30:00+00:00:30",
            "2026-10-06T16:30:00+0000",
            "2026-10-06T16:30:00+00:60",
            "2026-10-06T16:30:00+01:99",
        ):
            with self.subTest(timestamp=timestamp):
                with self.assertRaisesRegex(SquareResponseError, "^square_payment_refund_created_at_required$"):
                    canonical_square_refunds([return_order], [{**refund, "created_at": timestamp}])

        for timestamp in (
            "2026-10-06T16:30:00Z",
            "2026-10-06T16:30:00.123+02:00",
            "2026-10-06T16:30:00+23:59",
            "2026-10-06t16:30:00z",
        ):
            with self.subTest(timestamp=timestamp):
                records = canonical_square_refunds([return_order], [{**refund, "created_at": timestamp}])
                self.assertEqual(records[0]["occurred_at"], timestamp)


if __name__ == "__main__":
    unittest.main()
