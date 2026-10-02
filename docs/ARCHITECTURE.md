# Architecture and data integrity

[Home](../README.md) · [Roadmap](ROADMAP.md)

## Status and boundaries

The current state consists of **reference contracts, an offline validator, and an experimental read-only Loyverse transport**. It is not a running synchronization service, a canonical Loyverse normalizer, or a verified OpenRetailSchema POS integration. The Loyverse client has synthetic-response tests; independent live certification remains pending. Implementation claims must be backed by local tests, and vendor compatibility must be demonstrated with authorized test credentials outside the public repository.

## Data flow

1. **Connector:** retrieves or receives data using documented provider interfaces and declares individual supported capabilities. The initial Loyverse GET transport is experimental and yields raw dictionaries; it does not currently output canonical records.
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

Monetary values use decimal **strings** with three-letter uppercase currency codes, not floating-point JSON numbers. The v0.1 schema validates the code shape (`^[A-Z]{3}$`) but does **not** embed an ISO 4217 registry or claim that every syntactically valid code is supported by a connector or consumer. Connectors must preserve a documented source currency, must not infer one from country or locale, and must treat a currency they cannot map safely as unsupported rather than substituting a default. Within one canonical sale, every reported monetary value must use the same currency; mixed-currency sales are rejected until the contract can represent distinct money roles without loss.

A sale's amounts are optional unless provided by the source. Refunds have their own `sale_kind`, and signed amounts and quantities preserve the source convention. No formula or rounding is implied.

An activity metric stores offset-aware `interval_start` and `interval_end`, plus an optional store timezone. The schema validates timestamp format, while the offline validator also rejects intervals whose end instant is not after their start instant. Consumers must not infer business-day boundaries or aggregation completeness from those checks, and must not assume customer counts from transaction counts.

## Connector capability contract (proposed)

Each adapter must expose a stable provider ID and capabilities for individual resources and operations (for example `sales.read`, `products.read`, `inventory.read`, `sales.events`, or `prices.write`). Missing resources and inaccessible interfaces must be represented as unsupported, not silently fabricated.

Future sync requirements: pagination, retry and rate-limit handling, idempotent upserts, incremental checkpoints, data-deletion policy, store isolation, clock and DST handling, safe logging and secret storage. Outbound POS writes are out of scope for the initial read-only release.

## Validation

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/valid_sale.json
python -m unittest discover -s tests -v
```

These commands run locally. The repository also has a minimal GitHub Actions regression workflow; CI is evidence for the exact commit it tests, not a substitute for connector live testing.
