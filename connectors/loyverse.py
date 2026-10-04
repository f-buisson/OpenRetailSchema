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
import time
from datetime import datetime
from decimal import Decimal
from math import isfinite
from urllib.parse import urlencode

_LOYVERSE_HOST = "api.loyverse.com"
_COLLECTIONS = {"items": "items", "variants": "variants", "inventory": "inventory_levels", "taxes": "taxes", "stores": "stores", "receipts": "receipts", "employees": "employees", "pos_devices": "pos_devices", "shifts": "shifts"}
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024
_MAX_RETRY_AFTER_SECONDS = 5.0


class LoyverseError(Exception):
    """Safe-to-display error without token, URL query, or vendor response body."""
    def __init__(self, code: str, status: int | None = None, *, retry_after: float | None = None):
        super().__init__(code)
        self.code = code
        self.status = status
        self.retry_after = retry_after


def _bounded_retry_after(value: str | None) -> float | None:
    """Accept only a finite, short Retry-After delta; ignore unsafe input."""
    if value is None:
        return None
    try:
        delay = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(delay) or delay < 0 or delay > _MAX_RETRY_AFTER_SECONDS:
        return None
    return delay


def _transport(path: str, token: str) -> dict:
    """Read an official Loyverse endpoint; do not follow redirects."""
    conn = http.client.HTTPSConnection(_LOYVERSE_HOST, timeout=20)
    try:
        conn.request("GET", path, headers={"Authorization": "Bearer " + token, "Accept": "application/json", "User-Agent": "OpenRetailSchema/0.1"})
        response = conn.getresponse()
        if not (200 <= response.status < 300):
            error = _http_error(response.status)
            if response.status == 429:
                error.retry_after = _bounded_retry_after(response.getheader("Retry-After"))
            raise error
        payload = response.read(_MAX_RESPONSE_BYTES + 1)
        if len(payload) > _MAX_RESPONSE_BYTES:
            raise LoyverseError("response_too_large")
        try:
            value = json.loads(payload.decode("utf-8"), parse_float=Decimal)
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise LoyverseError("invalid_json") from None
        if not isinstance(value, dict):
            raise LoyverseError("unexpected_payload")
        return value
    except (OSError, TimeoutError):
        raise LoyverseError("connection_failure") from None
    finally:
        conn.close()


def _http_error(status: int) -> LoyverseError:
    error_codes = {400: "bad_request", 401: "unauthorized", 402: "plan_restricted_history", 403: "forbidden", 404: "not_found", 429: "rate_limited"}
    return LoyverseError(error_codes.get(status, "provider_http_error"), status=status)


def _retryable(error: LoyverseError) -> bool:
    if error.code in {"connection_failure", "rate_limited"}:
        return True
    return error.code == "provider_http_error" and error.status is not None and 500 <= error.status < 600


class LoyverseClient:
    """Read-only transport with bounded GET retries and explicit page limits."""
    def __init__(self, token: str, *, transport=None, max_attempts: int = 3, sleeper=None):
        if not isinstance(token, str) or not token.strip() or "\n" in token or "\r" in token:
            raise ValueError("A non-empty token without newlines is required")
        if type(max_attempts) is not int or not 1 <= max_attempts <= 5:
            raise ValueError("max_attempts must be between 1 and 5")
        self._token = token
        self._send = transport if transport is not None else _transport
        self._max_attempts = max_attempts
        self._sleep = sleeper if sleeper is not None else time.sleep

    @classmethod
    def from_environment(cls):
        return cls(os.environ.get("LOYVERSE_API_TOKEN", ""))

    def _get(self, path: str) -> dict:
        """Execute one logical GET with a finite retry budget."""
        for attempt in range(1, self._max_attempts + 1):
            try:
                return self._send(path, self._token)
            except LoyverseError as error:
                if not _retryable(error) or attempt == self._max_attempts:
                    raise
                delay = error.retry_after if error.retry_after is not None else 0.0
                if delay:
                    self._sleep(delay)
        raise LoyverseError("retry_exhausted")

    def merchant(self) -> dict:
        result = self._get("/v1.0/merchant")
        if not isinstance(result, dict):
            raise LoyverseError("unexpected_payload")
        return result

    def iter_collection(self, resource: str, *, limit: int = 250, max_pages: int = 100, params: dict | None = None):
        """Yield raw records; each GET has a finite retry budget."""
        if resource not in _COLLECTIONS:
            raise ValueError("Unsupported resource")
        if type(limit) is not int or not 1 <= limit <= 250:
            raise ValueError("limit must be between 1 and 250")
        if type(max_pages) is not int or max_pages < 1:
            raise ValueError("max_pages must be a positive integer")
        if params is not None and (not isinstance(params, dict) or "cursor" in params or "limit" in params):
            raise ValueError("params must not override pagination")
        arguments = dict(params or {})
        cursor = None
        seen = set()
        for _ in range(max_pages):
            query = {"limit": limit, **arguments}
            if cursor is not None:
                query["cursor"] = cursor
            path = "/v1.0/" + resource + "?" + urlencode(query)
            response = self._get(path)
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


def source_decimal(record: dict, field: str) -> Decimal | None:
    """Preserve a finite numeric source value without guessing missing values."""
    if not isinstance(record, dict) or not isinstance(field, str) or field not in record:
        return None
    value = record[field]
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, Decimal):
        return value if value.is_finite() else None
    if type(value) is int:
        return Decimal(value)
    return None


def source_external_id(record: dict) -> str | None:
    """Return an opaque vendor id without coercing or rewriting it."""
    if not isinstance(record, dict) or "id" not in record:
        return None
    value = record["id"]
    if not isinstance(value, str) or not value.strip():
        return None
    return value


def canonical_money(record: dict, field: str, merchant: dict) -> dict | None:
    """Compose validated source amount and merchant currency into v0.1 money."""
    amount = source_decimal(record, field)
    currency = merchant_currency(merchant)
    if amount is None or currency is None:
        return None
    return {"amount": format(amount, "f"), "currency": currency}


def canonical_product(variant: dict, merchant: dict) -> dict:
    """Map one fabricated-compatible Loyverse variant to a canonical product."""
    external_id = source_external_id(variant)
    if external_id is None:
        raise LoyverseError("invalid_product_identity")
    name = variant.get("name") if isinstance(variant, dict) else None
    if not isinstance(name, str) or not name.strip():
        raise LoyverseError("invalid_product_name")
    optional = {}
    for field in ("sku", "barcode"):
        if field not in variant or variant[field] is None:
            continue
        value = variant[field]
        if not isinstance(value, str) or not value.strip():
            raise LoyverseError("invalid_product_" + field)
        optional[field] = value
    record = {"schema_version": "0.1.0", "entity_type": "product", "id": "loyverse:variant:" + external_id, "source": {"provider": "loyverse", "external_id": external_id}, "name": name, **optional}
    price = canonical_money(variant, "price", merchant)
    if price is not None:
        record["sale_price"] = price
    return record


def _opaque_string(record: dict, field: str) -> str | None:
    if not isinstance(record, dict) or field not in record:
        return None
    value = record[field]
    return value if isinstance(value, str) and value.strip() else None


def _event_timestamp(record: dict, field: str) -> str | None:
    value = _opaque_string(record, field)
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return value if parsed.tzinfo is not None and parsed.utcoffset() is not None else None


def canonical_sale(receipt: dict, merchant: dict) -> dict:
    """Map a documented-compatible Loyverse receipt to one canonical v0.1 sale.

    Loyverse documents ``SALE``/``REFUND`` explicitly and reports refund money
    as the amount returned to the customer. Values and signs are preserved; the
    transaction direction is represented by ``sale_kind`` rather than invented
    negation. ``total_money`` is deliberately not mapped to canonical
    ``gross_total`` because the vendor defines it as the paid/returned amount
    after discounts, taxes, surcharges and tips, which is not the same semantic.
    """
    receipt_number = _opaque_string(receipt, "receipt_number")
    if receipt_number is None:
        raise LoyverseError("invalid_sale_identity")
    store_id = _opaque_string(receipt, "store_id")
    if store_id is None:
        raise LoyverseError("invalid_sale_store")
    occurred_at = _event_timestamp(receipt, "receipt_date")
    if occurred_at is None:
        raise LoyverseError("invalid_sale_time")
    receipt_type = receipt.get("receipt_type") if isinstance(receipt, dict) else None
    kinds = {"SALE": "sale", "REFUND": "refund"}
    if receipt_type not in kinds:
        raise LoyverseError("invalid_sale_kind")
    source_lines = receipt.get("line_items") if isinstance(receipt, dict) else None
    if not isinstance(source_lines, list) or not source_lines:
        raise LoyverseError("invalid_sale_lines")
    lines = []
    for line in source_lines:
        line_id = _opaque_string(line, "id")
        variant_id = _opaque_string(line, "variant_id")
        quantity = source_decimal(line, "quantity")
        if line_id is None or variant_id is None or quantity is None:
            raise LoyverseError("invalid_sale_line")
        canonical_line = {"id": "loyverse:line:" + line_id, "source_product_id": variant_id, "quantity": format(quantity, "f")}
        gross = canonical_money(line, "gross_total_money", merchant)
        if gross is not None:
            canonical_line["gross_total"] = gross
        lines.append(canonical_line)
    record = {"schema_version": "0.1.0", "entity_type": "sale", "id": "loyverse:receipt:" + receipt_number, "source": {"provider": "loyverse", "external_id": receipt_number}, "store_id": store_id, "occurred_at": occurred_at, "sale_kind": kinds[receipt_type], "lines": lines}
    tax = canonical_money(receipt, "total_tax", merchant)
    if tax is not None:
        record["tax_total"] = tax
    return record
