# Synthetic sales/activity CSV fixtures

These files are fabricated contract fixtures for future CSV import work. They contain no real POS, customer or employee data and do not certify an importer.

- `sales_contract_cases.csv` includes a normal sale, a refund with an explicitly negative reported total, and a row where the total is absent. The empty total means unknown/absent, never zero.
- `activity_dst_cases.csv` includes the Europe/Paris 2026 fall-back boundary with two equal wall-clock readings but different explicit offsets. The interval is ordered by absolute instant. It also includes an absent revenue value, which must not become zero.

The fixtures intentionally use offset-bearing RFC 3339 timestamps. A later fixture set should cover naive local input plus explicit timezone/disambiguation mapping, including rejection of spring-forward nonexistent times. Until an importer and mapping schema exist, these files are examples of required semantics rather than executable importer tests.
