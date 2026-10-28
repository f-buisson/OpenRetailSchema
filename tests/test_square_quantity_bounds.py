"""Square decimal quantity input must respect the documented 12-character limit.

Fabricated provider responses only; no credentials or real store data.
"""
import unittest

from connectors.square import (
    SquareResponseError,
    canonical_square_refunds,
    canonical_square_sales,
)


def sale(quantity: str):
    return [{
        "id": "order-1",
        "state": "COMPLETED",
        "location_id": "location-1",
        "closed_at": "2026-10-06T12:34:56Z",
        "line_items": [{
            "uid": "line-1", "catalog_object_id": "variation-1",
            "quantity": quantity,
        }],
    }]


def refund_inputs(quantity: str):
    orders = [{
        "id": "refund-order-1",
        "location_id": "location-1",
        "returns": [{
            "source_order_id": "order-1",
            "return_line_items": [{
                "uid": "return-line-1",
                "source_line_item_uid": "line-1",
                "catalog_object_id": "variation-1",
                "quantity": quantity,
            }],
        }],
    }]
    refunds = [{
        "id": "payment-refund-1",
        "order_id": "refund-order-1",
        "status": "COMPLETED",
        "created_at": "2026-10-06T12:34:57Z",
        "location_id": "location-1",
    }]
    return orders, refunds


class SquareQuantityBoundsTests(unittest.TestCase):
    def test_sale_rejects_out_of_contract_quantities(self):
        # 1e100000 is only 8 input characters, but previously expanded
        # to 100001 output characters in Decimal fixed-point formatting.
        invalid = ("1e100000", "1e-100000", "1234567890123",
                   "1_0", " 2 ", "+2", "NaN", "0")
        for quantity in invalid:
            with self.subTest(quantity=quantity):
                with self.assertRaisesRegex(
                    SquareResponseError, "^square_order_line_quantity_required$"
                ):
                    canonical_square_sales(sale(quantity))

    def test_refund_rejects_out_of_contract_quantities(self):
        for quantity in ("1e100000", "1e-100000", "1234567890123", "1_0"):
            with self.subTest(quantity=quantity):
                orders, refunds = refund_inputs(quantity)
                with self.assertRaisesRegex(
                    SquareResponseError, "^square_return_quantity_required$"
                ):
                    canonical_square_refunds(orders, refunds)

    def test_valid_decimal_quantities_preserve_precision(self):
        for raw, expected in (("1", "1"), ("1.70000", "1.70000"),
                              (".50", "0.50"), ("123456789012", "123456789012")):
            with self.subTest(quantity=raw):
                self.assertEqual(
                    canonical_square_sales(sale(raw))[0]["lines"][0]["quantity"],
                    expected,
                )
                orders, refunds = refund_inputs(raw)
                self.assertEqual(
                    canonical_square_refunds(orders, refunds)[0]["lines"][0]["quantity"],
                    expected,
                )


if __name__ == "__main__":
    unittest.main()
