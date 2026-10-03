# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from importers.time_normalization import TimestampNormalizationError, normalize_timestamp


class TimestampNormalizationTests(unittest.TestCase):
    def test_explicit_offset_preserves_absolute_instant(self):
        normalized = normalize_timestamp("2026-10-25T02:15:00+02:00")
        self.assertEqual(
            datetime.fromisoformat(normalized).astimezone(timezone.utc),
            datetime(2026, 10, 25, 0, 15, tzinfo=timezone.utc),
        )

    def test_z_is_accepted_without_timezone_inference(self):
        self.assertEqual(
            normalize_timestamp("2026-10-25T00:15:00Z"),
            "2026-10-25T00:15:00+00:00",
        )

    def test_naive_timestamp_requires_explicit_timezone(self):
        with self.assertRaisesRegex(TimestampNormalizationError, "timezone_required"):
            normalize_timestamp("2026-02-10T12:30:00")

    def test_nonexistent_paris_spring_time_is_rejected(self):
        with self.assertRaisesRegex(TimestampNormalizationError, "nonexistent_local_time"):
            normalize_timestamp("2026-03-29T02:15:00", timezone_name="Europe/Paris")

    def test_ambiguous_paris_fallback_requires_occurrence(self):
        with self.assertRaisesRegex(TimestampNormalizationError, "ambiguous_local_time"):
            normalize_timestamp("2026-10-25T02:15:00", timezone_name="Europe/Paris")

    def test_both_paris_fallback_occurrences_are_distinct(self):
        first = normalize_timestamp(
            "2026-10-25T02:15:00", timezone_name="Europe/Paris", occurrence=1
        )
        second = normalize_timestamp(
            "2026-10-25T02:15:00", timezone_name="Europe/Paris", occurrence=2
        )
        self.assertEqual(first, "2026-10-25T02:15:00+02:00")
        self.assertEqual(second, "2026-10-25T02:15:00+01:00")
        self.assertNotEqual(
            datetime.fromisoformat(first).astimezone(timezone.utc),
            datetime.fromisoformat(second).astimezone(timezone.utc),
        )

    def test_occurrence_is_rejected_for_unambiguous_local_time(self):
        with self.assertRaisesRegex(TimestampNormalizationError, "occurrence_not_applicable"):
            normalize_timestamp(
                "2026-02-10T12:30:00", timezone_name="Europe/Paris", occurrence=1
            )

    def test_disambiguation_is_rejected_for_offset_aware_input(self):
        with self.assertRaisesRegex(
            TimestampNormalizationError, "unexpected_timezone_disambiguation"
        ):
            normalize_timestamp(
                "2026-10-25T02:15:00+02:00", timezone_name="Europe/Paris"
            )

    def test_unknown_iana_timezone_is_rejected(self):
        with self.assertRaisesRegex(TimestampNormalizationError, "invalid_timezone"):
            normalize_timestamp("2026-02-10T12:30:00", timezone_name="Not/AZone")


if __name__ == "__main__":
    unittest.main()
