# Synthetic sales/activity CSV fixtures

These files are fabricated contract fixtures for future CSV import work. They contain no real POS, customer or employee data and do not certify an importer.

- `sales_contract_cases.csv` includes a normal sale, a refund with an explicitly negative reported total, and a row where the total is absent. The empty total means unknown/absent, never zero.
- `activity_dst_cases.csv` includes the Europe/Paris 2026 fall-back boundary with two equal wall-clock readings but different explicit offsets. The interval is ordered by absolute instant. It also includes an absent revenue value, which must not become zero.
- `activity_local_dst_cases.csv` covers naive local wall-clock input under an explicitly configured `Europe/Paris` timezone. `activity-spring-nonexistent` must be rejected because `2026-03-29T02:15:00` does not exist in that zone. `activity-fallback-explicit` supplies `+02:00` then `+01:00` to disambiguate the repeated fall-back hour and therefore identifies two distinct instants. `activity-fallback-ambiguous` omits disambiguation during that repeated hour and must be rejected rather than silently choosing an occurrence.

The fixtures deliberately keep offset-bearing input separate from naive local input. Local timestamps are valid source text only when the mapping explicitly supplies an IANA timezone, and ambiguous fall-back values additionally require disambiguation. Until an importer and mapping schema exist, these files are examples of required semantics rather than executable importer tests.
