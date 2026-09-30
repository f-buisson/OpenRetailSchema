# SPDX-License-Identifier: Apache-2.0
"""Experimental read-only Loyverse v1.0 client; no live integration certification.

Only documented GET resources are exposed. Personal access tokens grant broad
account access, even when this client is deliberately restricted to GET.
Use an authorized test account and keep credentials outside source control.
"""
from __future__ import annotations

import http.client
import json
import os
from decimal import Decimal
from urllib.parse import urlencode


# Fixed host and direct HTTPS requests prevent cross-origin credential redirects.
_LOYVERSE_HOST = "api.loyverse.com"
_COLLECTIONS = {
    "items": "items",
    "variants": "variants",
    "inventory": "inventory_levels",
    "taxes": "taxes",
    "stores": "stores",
    "receipts": "receipts",
    "employees": "employees",
    "pos_devices": "pos_devices",
    "shifts": "shifts",
}
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024


class LoyverseError(Exception):
    """Safe-to-display error without token, URL query, or vendor response body."""

    def __init__(self, code: str, status: int | None = None):
        super().__init__(code)
        self.code = code
        self.status = status


def _transport(path: str, token: str) -> dict:
    """Read an official Loyverse endpoint; do not follow redirects."""
    conn = http.client.HTTPSConnection(_LOYVERSE_HOST, timeout=20)
    try:
        conn.request(
            "GET",
            path,
            headers={
                "Authorization": "Bearer " + token,
                "Accept": "application/json",
                "User-Agent": "OpenRetailSchema/0.1",
            },
        )
        response = conn.getresponse()
        if not (200 <= response.status < 300):
            raise _http_error(response.status)
        payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise LoyverseError("response_too_large")
        try:
            # Preserve monetary precision until the normalizer decides units.
            value = json.loads(payload.decode("utf-8"), parse_float=Decimal)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LoyverseError("invalid_json") from None
        if not isinstance(value, dict):
            raise LoyverseError("unexpected_payload")
        return value
    except (OSError, TimeoutError) as exc:
        raise LoyverseError("connection_failure") from None
    finally:
        conn.close()


def _http_error(status: int) -> LoyverseError:
    error_codes = {
        400: "bad_request",
        401: "unauthorized",
        402: "plan_restricted_history",
        403: "forbidden",
        404: "not_found",
        429: "rate_limited",
    }
    return LoyverseError(error_codes.get(status, "provider_http_error"), status=status)


class LoyverseClient:
    """Read-only transport with explicit page limits and injectable test I/O.

    This class yields *raw vendor dictionaries*, not canonical records.
    No token is stored on disk and no vendor payload is logged.
    """

    def __init__(self, token: str, *, transport=None):
        if not isinstance(token, str) or not token.strip() or "\n" in token or "\r" in token:
            raise ValueError("A non-empty token without newlines is required")
        self._token = token
        self._send = transport if transport is not None else _transport

    @classmethod
    def from_environment(cls):
        """Use LOYVERSE_API_TOKEN without placing credentials in CLI history."""
        return cls(os.environ.get("LOYVERSE_API_TOKEN", ""))

    def merchant(self) -> dict:
        result = self._send("/v1.0/merchant", self._token)
        if not isinstance(result, dict):
            raise LoyverseError("unexpected_payload")
        return result

    def iter_collection(self, resource: str, *, limit: int = 250,
                        max_pages: int = 100, params: dict | None = None):
        """Yield raw records; do not retry or infer records after provider errors."""
        if resource not in _COLLECTIONS:
            raise ValueError("Unsupported resource")
        if type(limit) is not int or not 1 <= limit <= 250:
            raise ValueError("limit must be between 1 and 250")
        if type(max_pages) is not int or max_pages < 1:
            raise ValueError("max_pages must be a positive integer")
        if params is not None and (
            not isinstance(params, dict) or "cursor" in params or "limit" in params
        ):
            raise ValueError("params must not override pagination")
        arguments = dict(params or {})
        cursor = None
        seen = set()
        for _ in range(max_pages):
            query = {"limit": limit, **arguments}
            if cursor is not None:
                query["cursor"] = cursor
            path = "/v1.0/" + resource + "?" + urlencode(query)
            response = self._send(path, self._token)
            if not isinstance(response, dict) or not isinstance(response.get(_COLLECTIONS[resource]), list):
                raise LoyverseError("unexpected_payload")
            for item in response[_COLLECTIONS[resource]]:
                if not isinstance(item, dict):
                    raise LoyverseError("unexpected_payload")
                yield item
            cursor = response.get("cursor")
            if cursor is None or cursor == "":
                return
            if not isinstance(cursor, str) or len(cursor) > 1024 or cursor in seen:
                raise LoyverseError("invalid_pagination_cursor")
            seen.add(cursor)
        raise LoyverseError("page_limit_reached")


def merchant_currency(merchant: dict) -> str | None:
    """Extract published merchant currency shapes without an invented fallback."""
    if not isinstance(merchant, dict):
        return None
    value = merchant.get("currency")
    if isinstance(value, dict):
        value = value.get("code")
    if isinstance(value, str) and len(value) == 3 and value.isalpha() and value.isupper():
        return value
    return None
