"""Synthetic regression for RFC 3339 fractions beyond Python's int string limit."""
import unittest

from jsonschema import FormatChecker
from scripts.validate import _exact_instant, semantic_errors


def interval_errors(start: str, end: str) -> list[str]:
    return semantic_errors({
        "entity_type": "activity_metric",
        "interval_start": start,
        "interval_end": end,
    })


class LongTimestampFractionTests(unittest.TestCase):
    def test_long_fraction_is_schema_valid_and_does_not_crash(self):
        start = "2026-10-06T12:34:56." + "1" * 4301 + "Z"
        self.assertTrue(FormatChecker().conforms(start, "date-time"))
        self.assertEqual(interval_errors(start, "2026-10-06T12:34:57Z"), [])

    def test_long_fraction_preserves_ordering(self):
        prefix = "2026-10-06T12:34:56."
        start = prefix + "1" * 4999 + "1Z"
        end = prefix + "1" * 4999 + "2Z"
        self.assertEqual(interval_errors(start, end), [])
        self.assertEqual(interval_errors(end, start), [
            "interval_end: must represent an instant after interval_start",
        ])

    def test_trailing_zeroes_preserve_equal_instant(self):
        short = "2026-10-06T12:34:56.1Z"
        long = "2026-10-06T12:34:56.1" + "0" * 5000 + "Z"
        self.assertEqual(_exact_instant(short), _exact_instant(long))
        self.assertEqual(interval_errors(short, long), [
            "interval_end: must represent an instant after interval_start",
        ])

    def test_regular_submicrosecond_ordering_unchanged(self):
        self.assertEqual(interval_errors(
            "2026-10-06T12:34:56.123456100Z",
            "2026-10-06T12:34:56.123456200Z",
        ), [])


if __name__ == "__main__":
    unittest.main()
