# SPDX-License-Identifier: Apache-2.0
"""Vendor-neutral timestamp normalization without silent timezone inference."""
from __future__ import annotations

from datetime import datetime, timezone as utc_timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


class TimestampError(ValueError):
    """Timestamp input is incomplete, invalid, nonexistent, or ambiguous."""


def _parse(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise TimestampError("invalid_timestamp")
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        raise TimestampError("invalid_timestamp") from None
    return parsed


def _valid_local_candidate(local: datetime, zone: ZoneInfo, fold: int) -> datetime | None:
    candidate = local.replace(tzinfo=zone, fold=fold)
    # A local wall time exists only if a UTC round-trip returns the same wall time.
    round_trip = candidate.astimezone(utc_timezone.utc).astimezone(zone)
    if round_trip.replace(tzinfo=None) != local or round_trip.fold != fold:
        return None
    return candidate


def normalize_timestamp(value: str, *, timezone: str | None = None,
                        occurrence: int | None = None) -> str:
    """Return an offset-bearing ISO timestamp while preserving the represented instant.

    Offset-bearing input is authoritative and never reinterpreted through ``timezone``.
    Naive local input requires an explicit IANA timezone. During a repeated wall time,
    ``occurrence=0`` selects the first occurrence and ``occurrence=1`` the second.
    """
    parsed = _parse(value)
    if parsed.tzinfo is not None:
        if parsed.utcoffset() is None:
            raise TimestampError("invalid_timestamp")
        if occurrence is not None:
            raise TimestampError("occurrence_not_applicable")
        return parsed.isoformat()

    if not isinstance(timezone, str) or not timezone.strip():
        raise TimestampError("timezone_required")
    try:
        zone = ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError, TypeError):
        raise TimestampError("invalid_timezone") from None

    candidates = [candidate for fold in (0, 1)
                  if (candidate := _valid_local_candidate(parsed, zone, fold)) is not None]
    if not candidates:
        raise TimestampError("nonexistent_local_time")

    # Outside a fallback overlap, fold=1 is not a distinct instant. Deduplicate it.
    distinct = {candidate.utcoffset(): candidate for candidate in candidates}
    if len(distinct) == 1:
        if occurrence is not None:
            raise TimestampError("occurrence_not_applicable")
        return candidates[0].isoformat()

    if occurrence not in (0, 1) or isinstance(occurrence, bool):
        raise TimestampError("ambiguous_local_time")
    selected = _valid_local_candidate(parsed, zone, occurrence)
    if selected is None:
        raise TimestampError("ambiguous_local_time")
    return selected.isoformat()
