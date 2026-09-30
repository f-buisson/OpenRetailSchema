# Architecture and data integrity

[Home](../README.md) · [Roadmap](ROADMAP.md)

## Status and boundaries

The current release is a **reference contract and an offline validator**, not a running synchronization service or a verified POS integration. Implementation claims must be backed by local tests, and vendor compatibility must be demonstrated with authorized test credentials outside the public repository.

## Data flow

1. **Connector:** retrieves or receives data using only verified provider interfaces and declares its capabilities.
2. **Raw store (planned):** retains a source payload securely, with strict access controls and retention rules. Raw payloads must never be committed here.
3. **Normalizer (planned):** maps supported source fields into canonical records; unknowns remain unknown.
4. **Validator (available):** validates canonical JSON records using the versioned schema.
5. **Consumer:** reads records with explicit source provenance and version metadata.

The public fixtures are synthetic. The optional `source.raw_ref` is a non-sensitive reference to a raw payload, **not** a guarantee that storage has been implemented.

## Version 0.1 record contract

The canonical file is `schemas/v0.1/record.schema.json` (JSON Schema Draft 2020-12). Initial entities: `sale`, `product`, `activity_metric`. This is an experimental compatibility contract; incompatible changes must be documented and versioned.

- `schema_version`: exact contract version for all initial records.
- `entity_type`: record kind; prevents ambiguous interpretation.
- `id`: canonical identifier; connectors must avoid collisions across providers and stores.
- `source.provider` and `source.external_id`: obligatory provenance.
- `source.observed_at`: optional actual observation time, distinct from a transaction's event time.
- `source.raw_ref`: optional non-sensitive reference; never insert credentials or full raw customer records.
- `extensions`: optional **namespaced** vendor fields (for example `examplepos:register_code`), without inventing universal semantics.

Monetary values use decimal **strings** with ISO 4217 currency codes, not floating-point JSON numbers. A sale's amounts are optional unless provided by the source. Refunds have their own `sale_kind`, and signed amounts and quantities preserve the source convention. No formula or rounding is implied.

An activity metric stores offset-aware `interval_start` and `interval_end`, plus an optional store timezone. The schema validates timestamp format, not chronological ordering, business-day boundaries, or whether aggregation from vendor events is complete. Consumers must not assume customer counts from transaction counts.

## Connector capability contract (proposed)

Each adapter must expose a stable provider ID and capabilities for individual resources and operations (for example `sales.read`, `products.read`, `inventory.read`, `sales.events`, or `prices.write`). Missing resources and inaccessible interfaces must be represented as unsupported, not silently fabricated.

Future sync requirements: pagination, retry and rate-limit handling, idempotent upserts, incremental checkpoints, data-deletion policy, store isolation, clock and DST handling, safe logging and secret storage. Outbound POS writes are out of scope for the initial read-only release.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/valid_sale.json
python -m unittest discover -s tests -v
```

This runs locally. No hosted workflow is configured.
