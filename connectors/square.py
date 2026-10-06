# SPDX-License-Identifier: Apache-2.0
"""Synthetic-testable Square read connector foundation.

The connector intentionally uses an injected transport. It contains no credentials,
SDK dependency, or live-account claim. Endpoint choices are limited to Square's
public read APIs. Canonical product normalization is deliberately conservative:
missing provider values remain absent rather than becoming zero or empty strings.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from connectors.capabilities import capability_manifest
from connectors.operations import require_read_operation


SQUARE_API_VERSION = "2026-09-16"
SQUARE_CAPABILITIES = capability_manifest("square", {
    "products.read": "supported",
    "sales.read": "supported",
    "stores.read": "supported",
    "inventory.read": "supported",
})

Transport = Callable[[str, str, dict[str, Any]], dict[str, Any]]
Sleeper = Callable[[float], None]


class SquareResponseError(RuntimeError):
    """Raised when a synthetic or live transport returns an invalid response."""


class SquareConnector:
    """Expose the minimum Square read surface through the common contract."""

    manifest = SQUARE_CAPABILITIES

    def __init__(self, transport: Transport, *, max_retries: int = 2, sleeper: Sleeper | None = None):
        if not callable(transport):
            raise TypeError("transport_must_be_callable")
        if not isinstance(max_retries, int) or isinstance(max_retries, bool) or max_retries < 0:
            raise ValueError("max_retries_must_be_non_negative_integer")
        if sleeper is not None and not callable(sleeper):
            raise TypeError("sleeper_must_be_callable")
        self._transport = transport
        self._max_retries = max_retries
        self._sleeper = sleeper or (lambda _seconds: None)

    @staticmethod
    def _is_rate_limited(errors: Any) -> bool:
        return (
            isinstance(errors, list)
            and bool(errors)
            and all(isinstance(error, dict) and error.get("code") == "RATE_LIMITED" for error in errors)
        )

    def _request(self, method: str, path: str, *, params=None, body=None) -> dict[str, Any]:
        request: dict[str, Any] = {"api_version": SQUARE_API_VERSION}
        if params is not None:
            request["params"] = params
        if body is not None:
            request["json"] = body
        for attempt in range(self._max_retries + 1):
            response = self._transport(method, path, request)
            if not isinstance(response, dict):
                raise SquareResponseError("square_response_must_be_object")
            errors = response.get("errors")
            if not errors:
                return response
            if self._is_rate_limited(errors) and attempt < self._max_retries:
                self._sleeper(float(2 ** attempt))
                continue
            raise SquareResponseError("square_provider_error")
        raise AssertionError("unreachable_square_retry_loop")

    def _paginate_get(self, path: str, result_key: str, *, params=None, max_pages: int = 100) -> list[dict]:
        if max_pages < 1:
            raise ValueError("max_pages_must_be_positive")
        base = dict(params or {})
        cursor = None
        records: list[dict] = []
        for _ in range(max_pages):
            page_params = dict(base)
            if cursor:
                page_params["cursor"] = cursor
            response = self._request("GET", path, params=page_params)
            page = response.get(result_key, [])
            if not isinstance(page, list):
                raise SquareResponseError("square_result_must_be_array")
            records.extend(page)
            cursor = response.get("cursor")
            if not cursor:
                return records
            if not isinstance(cursor, str):
                raise SquareResponseError("square_cursor_must_be_string")
        raise SquareResponseError("square_pagination_limit_exceeded")

    def _paginate_post(self, path: str, result_key: str, *, body=None, max_pages: int = 100) -> list[dict]:
        if max_pages < 1:
            raise ValueError("max_pages_must_be_positive")
        base = dict(body or {})
        cursor = None
        records: list[dict] = []
        for _ in range(max_pages):
            page_body = dict(base)
            if cursor:
                page_body["cursor"] = cursor
            response = self._request("POST", path, body=page_body)
            page = response.get(result_key, [])
            if not isinstance(page, list):
                raise SquareResponseError("square_result_must_be_array")
            records.extend(page)
            cursor = response.get("cursor")
            if not cursor:
                return records
            if not isinstance(cursor, str):
                raise SquareResponseError("square_cursor_must_be_string")
        raise SquareResponseError("square_pagination_limit_exceeded")

    def read(self, operation: str, *, max_pages: int = 100) -> list[dict]:
        """Read one common operation without inventing canonical mappings."""
        require_read_operation(self.manifest, operation)
        if operation == "products.read":
            return self._paginate_get(
                "/v2/catalog/list",
                "objects",
                params={"types": "ITEM,ITEM_VARIATION"},
                max_pages=max_pages,
            )
        if operation == "sales.read":
            locations = self._paginate_get("/v2/locations", "locations", max_pages=max_pages)
            location_ids = [item.get("id") for item in locations if isinstance(item, dict) and item.get("id")]
            if not location_ids:
                return []
            records: list[dict] = []
            for offset in range(0, len(location_ids), 10):
                records.extend(self._paginate_post(
                    "/v2/orders/search",
                    "orders",
                    body={"location_ids": location_ids[offset:offset + 10], "return_entries": False},
                    max_pages=max_pages,
                ))
            return records
        if operation == "stores.read":
            return self._paginate_get("/v2/locations", "locations", max_pages=max_pages)
        if operation == "inventory.read":
            return self._paginate_post("/v2/inventory/counts/batch-retrieve", "counts", max_pages=max_pages)
        raise AssertionError("unreachable_common_read_operation")


def _required_nonempty_string(value: Any, code: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SquareResponseError(code)
    return value


def canonical_square_products(objects: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Map Square ITEM_VARIATION objects to canonical v0.1 products.

    A variation is the sellable Square product identity. Its parent ITEM supplies
    the canonical product name. Optional SKU/UPC values are copied only when
    present and non-empty. Price is intentionally not mapped here: Square Money
    uses integer minor units and converting that value requires currency exponent
    semantics that are outside this lot. Omitting it preserves absent/unknown != 0.
    """
    if not isinstance(objects, list):
        raise SquareResponseError("square_catalog_must_be_array")

    items: dict[str, dict[str, Any]] = {}
    variations: list[dict[str, Any]] = []
    for obj in objects:
        if not isinstance(obj, dict):
            raise SquareResponseError("square_catalog_object_must_be_object")
        object_type = obj.get("type")
        if object_type == "ITEM":
            item_id = _required_nonempty_string(obj.get("id"), "square_item_id_required")
            item_data = obj.get("item_data")
            if not isinstance(item_data, dict):
                raise SquareResponseError("square_item_data_required")
            items[item_id] = item_data
        elif object_type == "ITEM_VARIATION":
            variations.append(obj)

    records: list[dict[str, Any]] = []
    for variation in variations:
        external_id = _required_nonempty_string(variation.get("id"), "square_variation_id_required")
        data = variation.get("item_variation_data")
        if not isinstance(data, dict):
            raise SquareResponseError("square_variation_data_required")
        item_id = _required_nonempty_string(data.get("item_id"), "square_variation_item_id_required")
        parent = items.get(item_id)
        if parent is None:
            raise SquareResponseError("square_variation_parent_missing")
        name = _required_nonempty_string(parent.get("name"), "square_item_name_required")

        record: dict[str, Any] = {
            "schema_version": "0.1.0",
            "entity_type": "product",
            "id": "square:variation:" + external_id,
            "source": {"provider": "square", "external_id": external_id},
            "name": name,
        }
        for source_field, canonical_field in (("sku", "sku"), ("upc", "barcode")):
            value = data.get(source_field)
            if value is None:
                continue
            record[canonical_field] = _required_nonempty_string(
                value, "square_variation_" + source_field + "_invalid"
            )
        deleted = variation.get("is_deleted")
        if deleted is not None:
            if not isinstance(deleted, bool):
                raise SquareResponseError("square_variation_deleted_invalid")
            record["active"] = not deleted
        records.append(record)
    return records
