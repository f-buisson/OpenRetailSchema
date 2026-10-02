# SPDX-License-Identifier: Apache-2.0
"""Focused tests for explicit timestamp and DST normalization rules."""
import unittest
from datetime import datetime, timezone

from importers.timestamps import TimestampError, normalize_timestamp


class TimestampNormalizationTests(unittest.TestCase):
    def test_offset_bearing_input_preserves_absolute_instant(self):
        for source in ("2026-01-15T10:30:00Z", "2026-01-15T11:30:00+01:00"):
            with self.subTest(source=source):
                result = normalize_timestamp(source)
                parsed = datetime.fromisoformat(result)
                self.assertIsNotNone(parsed.utcoffset())
                self.assertEqual(
                    parsed.astimezone(timezone.utc),
                    datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc),
                )

    def test_naive_timestamp_requires_explicit_iana_timezone(self):
        with self.assertRaisesRegex(TimestampError, "timezone_required"):
            normalize_timestamp("2026-01-15T10:30:00")
        self.assertEqual(
            normalize_timestamp("2026-01-15T10:30:00", timezone="Europe/Paris"),
            "2026-01-15T10:30:00+01:00",
        )
        with self.assertRaisesRegex(TimestampError, "invalid_timezone"):
            normalize_timestamp("2026-01-15T10:30:00", timezone="Europe/Not_A_Zone")

    def test_spring_forward_nonexistent_wall_time_is_rejected(self):
        with self.assertRaisesRegex(TimestampError, "nonexistent_local_time"):
            normalize_timestamp("2026-03-29T02:15:00", timezone="Europe/Paris")

    def test_fallback_requires_disambiguation_and_distinguishes_occurrences(self):
        source = "2026-10-25T02:15:00"
        with self.assertRaisesRegex(TimestampError, "ambiguous_local_time"):
            normalize_timestamp(source, timezone="Europe/Paris")

        first = normalize_timestamp(source, timezone="Europe/Paris", occurrence=0)
        second = normalize_timestamp(source, timezone="Europe/Paris", occurrence=1)
        self.assertEqual(first, "2026-10-25T02:15:00+02:00")
        self.assertEqual(second, "2026-10-25T02:15:00+01:00")
        self.assertNotEqual(
            datetime.fromisoformat(first).astimezone(timezone.utc),
            datetime.fromisoformat(second).astimezone(timezone.utc),
        )

    def test_occurrence_is_not_accepted_when_it_cannot_disambiguate(self):
        with self.assertRaisesRegex(TimestampError, "occurrence_not_applicable"):
            normalize_timestamp(
                "2026-01-15T10:30:00", timezone="Europe/Paris", occurrence=0
            )
        with self.assertRaisesRegex(TimestampError, "occurrence_not_applicable"):
            normalize_timestamp("2026-01-15T10:30:00+01:00", occurrence=0)


if __name__ == "__main__":
    unittest.main()
