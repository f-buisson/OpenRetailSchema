# SPDX-License-Identifier: Apache-2.0
"""Vendor-neutral execution semantics shared by read-only connectors."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


ERROR_KINDS = frozenset({
    "authentication",
    "authorization",
    "entitlement",
    "rate_limit",
    "provider_unavailable",
    "invalid_request",
    "invalid_response",
})


@dataclass(frozen=True)
class PageState:
    """Ephemeral pagination state returned by one provider traversal."""

    cursor: Optional[str] = None
    has_more: bool = False

    def __post_init__(self) -> None:
        if self.has_more and not self.cursor:
            raise ValueError("pagination_cursor_required")
        if self.cursor is not None and not self.cursor.strip():
            raise ValueError("pagination_cursor_invalid")


@dataclass(frozen=True)
class Checkpoint:
    """Caller-owned durable source progress, never a pagination cursor."""

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value.strip():
            raise ValueError("checkpoint_invalid")


@dataclass(frozen=True)
class ConnectorFailure:
    """Stable failure classification exposed to connector consumers."""

    kind: str
    retryable: bool
    retry_after_seconds: Optional[float] = None

    def __post_init__(self) -> None:
        if self.kind not in ERROR_KINDS:
            raise ValueError("connector_error_kind_invalid")
        if self.retry_after_seconds is not None:
            if self.kind != "rate_limit":
                raise ValueError("retry_after_requires_rate_limit")
            if self.retry_after_seconds < 0:
                raise ValueError("retry_after_invalid")
        if self.kind in {"authentication", "authorization", "entitlement", "invalid_request", "invalid_response"} and self.retryable:
            raise ValueError("permanent_connector_error_cannot_retry")


def classify_http_failure(status: int, retry_after_seconds: Optional[float] = None) -> ConnectorFailure:
    """Map common HTTP outcomes to stable vendor-neutral failure semantics."""
    if status == 401:
        return ConnectorFailure("authentication", False)
    if status == 402:
        return ConnectorFailure("entitlement", False)
    if status == 403:
        return ConnectorFailure("authorization", False)
    if status == 429:
        return ConnectorFailure("rate_limit", True, retry_after_seconds)
    if 500 <= status <= 599:
        return ConnectorFailure("provider_unavailable", True)
    if 400 <= status <= 499:
        return ConnectorFailure("invalid_request", False)
    raise ValueError("http_status_not_failure")
