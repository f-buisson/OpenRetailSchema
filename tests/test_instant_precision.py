"""Issue #50: interval ordering must not truncate fractional seconds.

Synthetic timestamps only.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.validate import _exact_instant, semantic_errors  # noqa: E402


def accepted(start: str, end: str) -> bool:
    return not semantic_errors({
        "entity_type": "activity_metric", "interval_start": start, "interval_end": end,
    })


class SubMicrosecondOrderingTests(unittest.TestCase):
    def test_increasing_intervals_within_one_microsecond_are_accepted(self):
        self.assertTrue(accepted("2026-10-06T12:34:56.123456100Z", "2026-10-06T12:34:56.123456200Z"))
        self.assertTrue(accepted("2026-10-06T12:34:56.123456001Z", "2026-10-06T12:34:56.123456999Z"))
        self.assertTrue(accepted("2026-10-06T12:34:56.123456000Z", "2026-10-06T12:34:56.123457000Z"))

    def test_decreasing_or_equal_intervals_are_rejected(self):
        self.assertFalse(accepted("2026-10-06T12:34:56.123456200Z", "2026-10-06T12:34:56.123456100Z"))
        self.assertFalse(accepted("2026-10-06T12:34:56.1234561Z", "2026-10-06T12:34:56.123456100Z"),
                         "trailing zeros denote the same instant")

    def test_offsets_are_compared_as_instants(self):
        self.assertTrue(accepted("2026-10-06T14:34:56.000000001+02:00", "2026-10-06T12:34:56.000000002Z"))
        self.assertFalse(accepted("2026-10-06T12:34:56.5Z", "2026-10-06T14:34:56.5+02:00"))

    def test_exact_instant_keeps_every_digit(self):
        a = _exact_instant("2026-10-06T12:34:56.123456100Z")
        b = _exact_instant("2026-10-06T12:34:56.123456200Z")
        self.assertLess(a, b)
        self.assertEqual(b - a, _exact_instant("1970-01-01T00:00:00.0000001Z"))

    def test_non_rfc3339_iso_forms_keep_the_previous_path(self):
        self.assertIsNone(_exact_instant("2026-10-06 12:34:56Z"))
        self.assertTrue(accepted("2026-10-06T12:34:56+00:00", "2026-10-06T12:34:57+00:00"))


if __name__ == "__main__":
    unittest.main()
