# SPDX-License-Identifier: Apache-2.0
"""Synthetic tests for caller-owned Loyverse incremental checkpoints."""
import unittest
from urllib.parse import parse_qs, urlsplit

from connectors.loyverse import LoyverseClient, LoyverseError


class LoyverseCheckpointTests(unittest.TestCase):
    def test_initial_sync_advances_to_latest_source_update(self):
        calls = []
        def transport(path, token):
            calls.append(path)
            return {"items": [
                {"id": "a", "updated_at": "2026-10-04T10:00:00Z"},
                {"id": "b", "updated_at": "2026-10-04T12:00:00+00:00"},
            ]}
        rows, checkpoint = LoyverseClient("synthetic-token", transport=transport).read_incremental("items")
        self.assertEqual([row["id"] for row in rows], ["a", "b"])
        self.assertEqual(checkpoint, "2026-10-04T12:00:00+00:00")
        self.assertNotIn("updated_at_min", calls[0])

    def test_resume_uses_checkpoint_not_pagination_cursor_and_is_monotonic(self):
        calls = []
        def transport(path, token):
            calls.append(path)
            query = parse_qs(urlsplit(path).query)
            if "cursor" not in query:
                return {"items": [{"id": "same", "updated_at": "2026-10-04T12:00:00Z"}], "cursor": "page-two"}
            return {"items": [{"id": "older", "updated_at": "2026-10-04T11:00:00+00:00"}]}
        checkpoint = "2026-10-04T12:00:00+00:00"
        rows, next_checkpoint = LoyverseClient("synthetic-token", transport=transport).read_incremental("items", checkpoint=checkpoint)
        self.assertEqual(len(rows), 2)
        self.assertEqual(next_checkpoint, checkpoint)
        first = parse_qs(urlsplit(calls[0]).query)
        second = parse_qs(urlsplit(calls[1]).query)
        self.assertEqual(first["updated_at_min"], [checkpoint])
        self.assertNotIn("cursor", first)
        self.assertEqual(second["cursor"], ["page-two"])
        self.assertEqual(second["updated_at_min"], [checkpoint])

    def test_missing_null_malformed_and_offsetless_updates_are_rejected(self):
        invalid = ({}, {"updated_at": None}, {"updated_at": ""}, {"updated_at": "0"}, {"updated_at": "2026-10-04T12:00:00"})
        for row in invalid:
            with self.subTest(row=row):
                client = LoyverseClient("synthetic-token", transport=lambda path, token, row=row: {"items": [row]})
                with self.assertRaisesRegex(LoyverseError, "invalid_checkpoint"):
                    client.read_incremental("items")

    def test_invalid_input_checkpoint_is_rejected_before_transport(self):
        calls = []
        client = LoyverseClient("synthetic-token", transport=lambda path, token: calls.append(path) or {"items": []})
        for checkpoint in ("", "0", "2026-10-04T12:00:00"):
            with self.subTest(checkpoint=checkpoint):
                with self.assertRaisesRegex(LoyverseError, "invalid_checkpoint"):
                    client.read_incremental("items", checkpoint=checkpoint)
        self.assertEqual(calls, [])

    def test_processing_failure_returns_no_checkpoint(self):
        client = LoyverseClient(
            "synthetic-token",
            transport=lambda path, token: {"items": [{"id": "a", "updated_at": "2026-10-04T12:00:00Z"}]},
        )
        def fail(_row):
            raise ValueError("synthetic processing failure")
        with self.assertRaisesRegex(ValueError, "synthetic processing failure"):
            client.read_incremental("items", checkpoint="2026-10-04T10:00:00Z", transform=fail)

    def test_traversal_failure_returns_no_checkpoint(self):
        def transport(path, token):
            if "cursor=" in path:
                raise LoyverseError("connection_failure")
            return {"items": [{"id": "a", "updated_at": "2026-10-04T12:00:00Z"}], "cursor": "next"}
        client = LoyverseClient("synthetic-token", transport=transport, max_attempts=1)
        with self.assertRaisesRegex(LoyverseError, "connection_failure"):
            client.read_incremental("items", checkpoint="2026-10-04T10:00:00Z")


    def test_failed_pagination_can_restart_from_the_same_durable_checkpoint(self):
        durable_checkpoint = "2026-10-04T10:00:00Z"
        run = 1
        calls = []

        def transport(path, token):
            self.assertEqual(token, "synthetic-token")
            query = parse_qs(urlsplit(path).query)
            calls.append((run, query))
            self.assertEqual(query["updated_at_min"], [durable_checkpoint])

            if "cursor" not in query:
                return {
                    "items": [{"id": "a", "updated_at": "2026-10-04T11:00:00Z"}],
                    "cursor": "page-two",
                }

            self.assertEqual(query["cursor"], ["page-two"])
            if run == 1:
                raise LoyverseError("connection_failure")
            return {"items": [{"id": "b", "updated_at": "2026-10-04T12:00:00Z"}]}

        client = LoyverseClient(
            "synthetic-token", transport=transport, max_attempts=1
        )
        with self.assertRaisesRegex(LoyverseError, "connection_failure"):
            client.read_incremental("items", checkpoint=durable_checkpoint)

        # A failed traversal cannot advance durable progress or retain its cursor.
        run = 2
        rows, checkpoint = client.read_incremental(
            "items", checkpoint=durable_checkpoint
        )
        self.assertEqual([row["id"] for row in rows], ["a", "b"])
        self.assertEqual(checkpoint, "2026-10-04T12:00:00Z")
        self.assertEqual([attempt for attempt, _ in calls], [1, 1, 2, 2])
        self.assertNotIn("cursor", calls[0][1])
        self.assertEqual(calls[1][1]["cursor"], ["page-two"])
        self.assertNotIn("cursor", calls[2][1])
        self.assertEqual(calls[3][1]["cursor"], ["page-two"])


if __name__ == "__main__":
    unittest.main()
