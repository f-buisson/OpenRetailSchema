# SPDX-License-Identifier: Apache-2.0
"""Vendor-neutral timestamp normalization with explicit timezone semantics."""
from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimestampNormalizationError(ValueError):
    """Raised when a timestamp cannot be normalized without guessing."""


def _parse_iso8601(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise TimestampNormalizationError("invalid_timestamp")
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as exc:
        raise TimestampNormalizationError("invalid_timestamp") from exc
    return parsed


def _valid_local_candidates(local: datetime, zone: ZoneInfo) -> list[datetime]:
    candidates: list[datetime] = []
    for fold in (0, 1):
        candidate = local.replace(tzinfo=zone, fold=fold)
        roundtrip = candidate.astimezone(timezone.utc).astimezone(zone)
        if roundtrip.replace(tzinfo=None) != local or roundtrip.fold != fold:
            continue
        if not any(existing.utcoffset() == candidate.utcoffset() for existing in candidates):
            candidates.append(candidate)
    return candidates


def normalize_timestamp(value: str, *, timezone_name: str | None = None,
                        occurrence: int | None = None) -> str:
    """Return an offset-aware ISO-8601 timestamp without inferring missing context.

    Offset-aware input is preserved as the same instant and does not require a
    timezone. Naive local input requires an explicit IANA timezone. If the wall
    time is repeated during a UTC-offset fallback, ``occurrence`` must be 1 or 2.
    """
    parsed = _parse_iso8601(value)

    if parsed.tzinfo is not None and parsed.utcoffset() is not None:
        if timezone_name is not None or occurrence is not None:
            raise TimestampNormalizationError("unexpected_timezone_disambiguation")
        return parsed.isoformat()

    if timezone_name is None:
        raise TimestampNormalizationError("timezone_required")
    if occurrence not in (None, 1, 2):
        raise TimestampNormalizationError("invalid_occurrence")

    try:
        zone = ZoneInfo(timezone_name)
    except (ZoneInfoNotFoundError, ValueError) as exc:
        raise TimestampNormalizationError("invalid_timezone") from exc

    candidates = _valid_local_candidates(parsed, zone)
    if not candidates:
        raise TimestampNormalizationError("nonexistent_local_time")
    if len(candidates) > 1:
        if occurrence is None:
            raise TimestampNormalizationError("ambiguous_local_time")
        return candidates[occurrence - 1].isoformat()
    if occurrence is not None:
        raise TimestampNormalizationError("occurrence_not_applicable")
    return candidates[0].isoformat()
