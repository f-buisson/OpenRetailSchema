# SPDX-License-Identifier: Apache-2.0
"""Loyverse reference implementation of the vendor-neutral connector contract."""
from __future__ import annotations

from connectors.capabilities import capability_manifest
from connectors.loyverse import LoyverseClient
from connectors.operations import require_read_operation


LOYVERSE_CAPABILITIES = capability_manifest("loyverse", {
    "products.read": "supported",
    "sales.read": "supported",
    "stores.read": "supported",
    "inventory.read": "supported",
})

_OPERATION_RESOURCES = {
    "products.read": "variants",
    "sales.read": "receipts",
    "stores.read": "stores",
    "inventory.read": "inventory",
}


class LoyverseConnector:
    """Expose Loyverse reads through the common operation contract.

    The adapter deliberately returns source dictionaries. Canonical product and
    sale normalization remains in ``connectors.loyverse``; stores and inventory
    have no canonical v0.1 entity and must not be fabricated as one.
    """

    manifest = LOYVERSE_CAPABILITIES

    def __init__(self, client: LoyverseClient):
        if not isinstance(client, LoyverseClient):
            raise TypeError("client_must_be_loyverse_client")
        self._client = client

    def read(self, operation: str, *, limit: int = 250, max_pages: int = 100) -> list[dict]:
        """Read one explicitly supported common operation to completion."""
        require_read_operation(self.manifest, operation)
        resource = _OPERATION_RESOURCES[operation]
        return list(self._client.iter_collection(resource, limit=limit, max_pages=max_pages))
