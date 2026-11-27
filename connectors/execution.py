# SPDX-License-Identifier: Apache-2.0
"""Vendor-neutral execution semantics shared by read-only connectors."""
from __future__ import annotations

import re
from dataclasses import dataclass
from math import isfinite
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
        if self.cursor is not None and not isinstance(self.cursor, str):
            raise ValueError("pagination_cursor_invalid")
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
            delay = self.retry_after_seconds
            if isinstance(delay, bool) or not isinstance(delay, (int, float)):
                raise ValueError("retry_after_invalid")
            try:
                finite = isfinite(delay)
            except OverflowError:
                finite = False
            if not finite or delay < 0:
                raise ValueError("retry_after_invalid")
        if self.kind in {"authentication", "authorization", "entitlement", "invalid_request", "invalid_response"} and self.retryable:
            raise ValueError("permanent_connector_error_cannot_retry")


READ_SCOPES = frozenset({"full", "incremental"})

_RELATED_DATA_NAME = re.compile(r"[a-z][a-z0-9_]*")

# Durable refusals of related data: the read may continue and name what is missing.
_DURABLE_RELATED_REFUSALS = frozenset({"authorization", "entitlement"})


@dataclass(frozen=True)
class ReadOutcome:
    """Completion record of one successful read traversal.

    A successful read is complete by definition: an adapter that cannot prove the
    end of its traversal (repeated cursor or page, exhausted page budget) fails
    instead of returning the records it saw. ``missing`` names related data that
    a durable refusal kept out of the read; a transient failure of related data
    fails the whole read instead (see ``related_data_may_be_missing``).
    """

    scope: str
    missing: tuple = ()
    checkpoint: Optional[Checkpoint] = None

    def __post_init__(self) -> None:
        if self.scope not in READ_SCOPES:
            raise ValueError("read_scope_invalid")
        if not isinstance(self.missing, tuple):
            raise ValueError("read_missing_invalid")
        for name in self.missing:
            if not isinstance(name, str) or _RELATED_DATA_NAME.fullmatch(name) is None:
                raise ValueError("read_missing_invalid")
        if len(set(self.missing)) != len(self.missing):
            raise ValueError("read_missing_duplicated")
        if self.checkpoint is not None and not isinstance(self.checkpoint, Checkpoint):
            raise ValueError("checkpoint_invalid")

    @property
    def proves_absence(self) -> bool:
        """Only a full traversal may justify treating an unseen record as removed."""
        return self.scope == "full"


def related_data_may_be_missing(failure: ConnectorFailure) -> bool:
    """Decide how a failed read of related data (taxes, stock, names) is reported.

    ``True``: a durable refusal; the read continues and names the data missing.
    ``False``: the whole read must fail with this failure. A transient failure
    reported as missing data would overwrite known values with unknown ones.
    """
    if not isinstance(failure, ConnectorFailure):
        raise ValueError("connector_failure_required")
    return failure.kind in _DURABLE_RELATED_REFUSALS


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
