import unittest

from connectors.loyverse import LoyverseClient, LoyverseError
from connectors.loyverse_contract import LoyverseConnector


class LoyverseContractTests(unittest.TestCase):
    def connector(self, responses):
        calls = []

        def transport(path, token):
            calls.append(path)
            if not responses:
                raise AssertionError("unexpected transport call")
            response = responses.pop(0)
            if isinstance(response, Exception):
                raise response
            return response

        client = LoyverseClient("synthetic-token", transport=transport, max_attempts=1)
        return LoyverseConnector(client), calls

    def test_manifest_declares_all_common_reads_explicitly_supported(self):
        connector, _ = self.connector([])
        self.assertEqual(connector.manifest["provider"], "loyverse")
        self.assertEqual(
            {name: value["support"] for name, value in connector.manifest["capabilities"].items()},
            {
                "products.read": "supported",
                "sales.read": "supported",
                "stores.read": "supported",
                "inventory.read": "supported",
            },
        )

    def test_products_read_uses_existing_paginated_variant_path(self):
        connector, calls = self.connector([
            {"variants": [{"id": "v1"}], "cursor": "next"},
            {"variants": [{"id": "v2"}]},
        ])
        self.assertEqual(connector.read("products.read", limit=2), [{"id": "v1"}, {"id": "v2"}])
        self.assertEqual(calls, ["/v1.0/variants?limit=2", "/v1.0/variants?limit=2&cursor=next"])

    def test_each_common_operation_maps_to_one_existing_loyverse_resource(self):
        cases = {
            "sales.read": ("receipts", "receipts"),
            "stores.read": ("stores", "stores"),
            "inventory.read": ("inventory", "inventory_levels"),
        }
        for operation, (resource, response_key) in cases.items():
            with self.subTest(operation=operation):
                connector, calls = self.connector([{response_key: [{"id": operation}]}])
                self.assertEqual(connector.read(operation), [{"id": operation}])
                self.assertEqual(calls, [f"/v1.0/{resource}?limit=250"])

    def test_non_contract_operation_is_rejected_without_transport(self):
        connector, calls = self.connector([])
        with self.assertRaisesRegex(ValueError, "unknown_common_read_operation"):
            connector.read("employees.read")
        self.assertEqual(calls, [])

    def test_provider_failure_is_not_hidden_by_contract_adapter(self):
        connector, calls = self.connector([LoyverseError("rate_limited", status=429)])
        with self.assertRaises(LoyverseError) as raised:
            connector.read("sales.read")
        self.assertEqual(raised.exception.code, "rate_limited")
        self.assertEqual(calls, ["/v1.0/receipts?limit=250"])


if __name__ == "__main__":
    unittest.main()
