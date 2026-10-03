# SPDX-License-Identifier: Apache-2.0
"""Executable regression checks for fabricated sales/activity CSV contracts."""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
import unittest

from importers.time_normalization import normalize_timestamp


FIXTURES = Path(__file__).resolve().parents[1] / "examples" / "csv"


def _rows(name: str) -> dict[str, dict[str, str]]:
    with (FIXTURES / name).open(encoding="utf-8", newline="") as handle:
        return {row["external_id"]: row for row in csv.DictReader(handle)}


class SalesActivityCsvFixtureTests(unittest.TestCase):
    def test_refund_preserves_explicit_negative_source_amount(self) -> None:
        refund = _rows("sales_contract_cases.csv")["refund-001"]

        self.assertEqual(refund["sale_kind"], "refund")
        self.assertEqual(refund["gross_total"], "-9.90")
        self.assertLess(float(refund["gross_total"]), 0)

    def test_missing_sale_total_remains_missing_not_zero(self) -> None:
        sale = _rows("sales_contract_cases.csv")["sale-missing-total"]

        self.assertEqual(sale["gross_total"], "")
        self.assertNotEqual(sale["gross_total"], "0")
        self.assertNotEqual(sale["gross_total"], "0.00")

    def test_missing_activity_revenue_remains_missing_not_zero(self) -> None:
        activity = _rows("activity_dst_cases.csv")["activity-missing-revenue"]

        self.assertEqual(activity["gross_revenue"], "")
        self.assertNotEqual(activity["gross_revenue"], "0")
        self.assertNotEqual(activity["gross_revenue"], "0.00")

    def test_dst_fallback_offsets_are_distinct_absolute_instants(self) -> None:
        activity = _rows("activity_dst_cases.csv")["activity-fallback"]

        start = normalize_timestamp(activity["interval_start"])
        end = normalize_timestamp(activity["interval_end"])
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)

        self.assertEqual(start, activity["interval_start"])
        self.assertEqual(end, activity["interval_end"])
        self.assertNotEqual(start_dt.timestamp(), end_dt.timestamp())
        self.assertEqual(end_dt.timestamp() - start_dt.timestamp(), 3600)


if __name__ == "__main__":
    unittest.main()
