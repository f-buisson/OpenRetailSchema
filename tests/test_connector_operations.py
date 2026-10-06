import unittest

from connectors.capabilities import capability_manifest
from connectors.operations import (
    COMMON_READ_OPERATIONS,
    UndeclaredOperationError,
    UnsupportedOperationError,
    require_read_operation,
)


class ConnectorOperationTests(unittest.TestCase):
    def test_common_read_operations_are_stable_vendor_neutral_names(self):
        self.assertEqual(COMMON_READ_OPERATIONS, frozenset({
            "products.read", "sales.read", "stores.read", "inventory.read",
        }))

    def test_explicitly_supported_operation_is_allowed(self):
        manifest = capability_manifest("example", {"products.read": "supported"})
        self.assertEqual(require_read_operation(manifest, "products.read"), "products.read")

    def test_explicitly_unsupported_operation_fails_with_stable_code(self):
        manifest = capability_manifest("example", {"inventory.read": "unsupported"})
        with self.assertRaises(UnsupportedOperationError) as raised:
            require_read_operation(manifest, "inventory.read")
        self.assertEqual(raised.exception.code, "connector_operation_unsupported")
        self.assertEqual(raised.exception.operation, "inventory.read")

    def test_absent_operation_remains_unknown_and_fails_differently(self):
        manifest = capability_manifest("example", {"products.read": "supported"})
        with self.assertRaises(UndeclaredOperationError) as raised:
            require_read_operation(manifest, "sales.read")
        self.assertEqual(raised.exception.code, "connector_operation_undeclared")
        self.assertEqual(raised.exception.operation, "sales.read")

    def test_non_contract_operation_is_rejected_before_manifest_lookup(self):
        manifest = capability_manifest("example", {"employees.read": "supported"})
        with self.assertRaisesRegex(ValueError, "unknown_common_read_operation"):
            require_read_operation(manifest, "employees.read")


if __name__ == "__main__":
    unittest.main()
