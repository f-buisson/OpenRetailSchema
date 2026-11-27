# SPDX-License-Identifier: Apache-2.0
"""Read completeness and related-data failure semantics (synthetic values only)."""
import unittest

from connectors.execution import (
    READ_SCOPES,
    Checkpoint,
    ConnectorFailure,
    ReadOutcome,
    classify_http_failure,
    related_data_may_be_missing,
)


class ReadOutcomeTests(unittest.TestCase):
    def test_only_a_full_read_proves_absence(self):
        self.assertEqual(READ_SCOPES, frozenset({"full", "incremental"}))
        self.assertTrue(ReadOutcome("full").proves_absence)
        # An incremental read returns what changed; an unseen record is unchanged, not removed.
        self.assertFalse(ReadOutcome("incremental", checkpoint=Checkpoint("2026-11-27T10:00:00Z")).proves_absence)

    def test_scope_is_explicit(self):
        for invalid in (None, "", "FULL", "partial", "snapshot", 1, True):
            with self.subTest(scope=invalid):
                with self.assertRaisesRegex(ValueError, "^read_scope_invalid$"):
                    ReadOutcome(invalid)

    def test_missing_names_are_explicit_stable_and_unique(self):
        self.assertEqual(ReadOutcome("full", ("tax_rates", "stock")).missing, ("tax_rates", "stock"))
        for invalid in (["tax_rates"], "tax_rates", ("",), (" stock",), ("Tax",), ("tax-rates",), ("1st",), (None,), ("\u0661",)):
            with self.subTest(missing=invalid):
                with self.assertRaisesRegex(ValueError, "^read_missing_invalid$"):
                    ReadOutcome("full", invalid)
        with self.assertRaisesRegex(ValueError, "^read_missing_duplicated$"):
            ReadOutcome("full", ("stock", "stock"))

    def test_checkpoint_is_a_checkpoint_never_a_raw_value(self):
        self.assertEqual(ReadOutcome("full", checkpoint=Checkpoint("v1")).checkpoint.value, "v1")
        for invalid in ("2026-11-27T10:00:00Z", 0, object()):
            with self.subTest(checkpoint=invalid):
                with self.assertRaisesRegex(ValueError, "^checkpoint_invalid$"):
                    ReadOutcome("incremental", checkpoint=invalid)


class RelatedDataFailureTests(unittest.TestCase):
    def test_durable_refusals_may_be_reported_as_missing_data(self):
        for status in (402, 403):
            with self.subTest(status=status):
                self.assertTrue(related_data_may_be_missing(classify_http_failure(status)))

    def test_transient_failures_fail_the_whole_read(self):
        # Reported as "tax rates missing", a 429 on the tax list would erase the
        # known rate of every record at the next full read.
        for failure in (classify_http_failure(429, 30), classify_http_failure(500), classify_http_failure(503)):
            with self.subTest(kind=failure.kind):
                self.assertTrue(failure.retryable)
                self.assertFalse(related_data_may_be_missing(failure))

    def test_other_permanent_failures_fail_the_whole_read(self):
        # A rejected credential or a malformed response is not a scoped refusal.
        for failure in (classify_http_failure(401), classify_http_failure(404), ConnectorFailure("invalid_response", False)):
            with self.subTest(kind=failure.kind):
                self.assertFalse(related_data_may_be_missing(failure))

    def test_requires_a_classified_failure(self):
        for invalid in (403, "authorization", None):
            with self.subTest(failure=invalid):
                with self.assertRaisesRegex(ValueError, "^connector_failure_required$"):
                    related_data_may_be_missing(invalid)


if __name__ == "__main__":
    unittest.main()
