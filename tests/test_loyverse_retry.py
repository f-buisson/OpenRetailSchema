# SPDX-License-Identifier: Apache-2.0
"""Synthetic tests for the bounded read-only Loyverse retry policy."""
import unittest

from connectors.loyverse import LoyverseClient, LoyverseError, _bounded_retry_after, _http_error


class LoyverseRetryTests(unittest.TestCase):
    def test_transient_failure_recovers_within_bound(self):
        calls = []

        def transport(path, token):
            calls.append((path, token))
            if len(calls) < 3:
                raise LoyverseError("connection_failure")
            return {"id": "synthetic-merchant"}

        client = LoyverseClient("synthetic-token", transport=transport, max_attempts=3)
        self.assertEqual(client.merchant(), {"id": "synthetic-merchant"})
        self.assertEqual(len(calls), 3)

    def test_transient_exhaustion_preserves_sanitized_classification(self):
        calls = []

        def transport(path, token):
            calls.append(path)
            raise LoyverseError("provider_http_error", status=503)

        client = LoyverseClient("synthetic-token", transport=transport, max_attempts=2)
        with self.assertRaises(LoyverseError) as ctx:
            client.merchant()
        self.assertEqual(ctx.exception.code, "provider_http_error")
        self.assertEqual(ctx.exception.status, 503)
        self.assertEqual(len(calls), 2)
        self.assertNotIn("synthetic-token", str(ctx.exception))

    def test_permanent_access_errors_are_not_retried(self):
        for status in (401, 402, 403):
            with self.subTest(status=status):
                calls = []

                def transport(path, token, status=status):
                    calls.append(path)
                    raise _http_error(status)

                client = LoyverseClient("synthetic-token", transport=transport, max_attempts=5)
                with self.assertRaises(LoyverseError) as ctx:
                    client.merchant()
                self.assertEqual(ctx.exception.status, status)
                self.assertEqual(len(calls), 1)

    def test_rate_limit_retry_uses_only_bounded_delay(self):
        sleeps = []
        calls = []

        def transport(path, token):
            calls.append(path)
            if len(calls) == 1:
                raise LoyverseError("rate_limited", status=429, retry_after=2.5)
            return {"id": "synthetic-merchant"}

        client = LoyverseClient("synthetic-token", transport=transport, max_attempts=2, sleeper=sleeps.append)
        self.assertEqual(client.merchant(), {"id": "synthetic-merchant"})
        self.assertEqual(sleeps, [2.5])
        self.assertEqual(len(calls), 2)

    def test_retry_after_parser_rejects_unbounded_or_malformed_values(self):
        self.assertEqual(_bounded_retry_after("0"), 0.0)
        self.assertEqual(_bounded_retry_after("5"), 5.0)
        for value in (None, "", "later", "-1", "5.1", "999999", "nan", "inf"):
            with self.subTest(value=value):
                self.assertIsNone(_bounded_retry_after(value))

    def test_retry_attempt_bound_is_small_and_explicit(self):
        for value in (0, 6, True, 1.5):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    LoyverseClient("synthetic-token", max_attempts=value)


if __name__ == "__main__":
    unittest.main()
