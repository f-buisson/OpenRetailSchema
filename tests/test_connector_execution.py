# SPDX-License-Identifier: Apache-2.0
import unittest

from connectors.execution import (
    Checkpoint,
    ConnectorFailure,
    PageState,
    classify_http_failure,
)


class ConnectorExecutionTests(unittest.TestCase):
    def test_pagination_cursor_is_ephemeral_and_required_only_when_more_exists(self):
        self.assertEqual(PageState().cursor, None)
        self.assertEqual(PageState(cursor="next", has_more=True).cursor, "next")
        with self.assertRaisesRegex(ValueError, "pagination_cursor_required"):
            PageState(has_more=True)
        with self.assertRaisesRegex(ValueError, "pagination_cursor_invalid"):
            PageState(cursor="   ")

    def test_checkpoint_is_explicit_caller_owned_progress(self):
        self.assertEqual(Checkpoint("2026-10-06T00:00:00Z").value, "2026-10-06T00:00:00Z")
        for invalid in ("", "   "):
            with self.assertRaisesRegex(ValueError, "checkpoint_invalid"):
                Checkpoint(invalid)

    def test_http_failures_have_stable_retry_semantics(self):
        expected = {
            401: ("authentication", False),
            402: ("entitlement", False),
            403: ("authorization", False),
            429: ("rate_limit", True),
            500: ("provider_unavailable", True),
            503: ("provider_unavailable", True),
            404: ("invalid_request", False),
        }
        for status, outcome in expected.items():
            failure = classify_http_failure(status)
            self.assertEqual((failure.kind, failure.retryable), outcome)

    def test_rate_limit_retry_after_is_explicit_and_non_negative(self):
        failure = classify_http_failure(429, 2.5)
        self.assertEqual(failure.retry_after_seconds, 2.5)
        with self.assertRaisesRegex(ValueError, "retry_after_invalid"):
            classify_http_failure(429, -1)
        with self.assertRaisesRegex(ValueError, "retry_after_requires_rate_limit"):
            ConnectorFailure("provider_unavailable", True, 1)

    def test_permanent_failures_cannot_be_marked_retryable(self):
        for kind in ("authentication", "authorization", "entitlement", "invalid_request", "invalid_response"):
            with self.assertRaisesRegex(ValueError, "permanent_connector_error_cannot_retry"):
                ConnectorFailure(kind, True)

    def test_non_failure_status_is_rejected(self):
        for status in (200, 301):
            with self.assertRaisesRegex(ValueError, "http_status_not_failure"):
                classify_http_failure(status)


if __name__ == "__main__":
    unittest.main()
