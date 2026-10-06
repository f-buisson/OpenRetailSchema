# SPDX-License-Identifier: Apache-2.0
"""Synthetic-testable Square read connector foundation.

The connector intentionally uses an injected transport. It contains no credentials,
SDK dependency, or live-account claim. Endpoint choices are limited to Square's
public read APIs and keep provider dictionaries unnormalized until canonical
semantics are defined and tested.
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
    """Expose the minimum Square read surface through the common contract.

    ``transport(method, path, request)`` is injected by the caller. ``request``
    contains either ``params`` or ``json`` and always includes ``api_version``.
    The connector does not own authentication and never logs transport payloads.

    Square ``RATE_LIMITED`` responses are retried only for these read operations.
    Retry count is bounded and delay is injected so tests never sleep.
    """

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
