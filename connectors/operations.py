# SPDX-License-Identifier: Apache-2.0
"""Vendor-neutral connector read-operation contract."""
from __future__ import annotations

from connectors.capabilities import capability_support

COMMON_READ_OPERATIONS = frozenset({
    "products.read",
    "sales.read",
    "stores.read",
    "inventory.read",
})


class ConnectorOperationError(RuntimeError):
    """Base error for an operation that cannot be invoked from its manifest."""

    def __init__(self, operation: str, code: str):
        super().__init__(code)
        self.operation = operation
        self.code = code


class UnsupportedOperationError(ConnectorOperationError):
    """Raised when a connector explicitly declares an operation unsupported."""

    def __init__(self, operation: str):
        super().__init__(operation, "connector_operation_unsupported")


class UndeclaredOperationError(ConnectorOperationError):
    """Raised when support is unknown because the operation is absent."""

    def __init__(self, operation: str):
        super().__init__(operation, "connector_operation_undeclared")


def require_read_operation(manifest: dict, operation: str) -> str:
    """Require explicit support before a common read operation is invoked.

    Explicitly unsupported and absent/unknown capabilities remain distinct so a
    caller never guesses that an undeclared operation is safe or unsupported.
    """
    if operation not in COMMON_READ_OPERATIONS:
        raise ValueError("unknown_common_read_operation")
    support = capability_support(manifest, operation)
    if support == "supported":
        return operation
    if support == "unsupported":
        raise UnsupportedOperationError(operation)
    raise UndeclaredOperationError(operation)
