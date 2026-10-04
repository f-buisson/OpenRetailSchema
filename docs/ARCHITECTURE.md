# Architecture and data integrity

[Home](../README.md) · [Roadmap](ROADMAP.md)

## Status and boundaries

The current state consists of **reference contracts, an offline validator, and an experimental read-only Loyverse transport with synthetic-tested product and sale normalization**. It is not a running synchronization service or a verified live OpenRetailSchema POS integration. The Loyverse client and its current canonical product/sale mappings have synthetic tests; independent live connector certification remains pending. Implementation claims must be backed by repository tests, and vendor compatibility must be demonstrated with authorized test credentials outside the public repository.

## Data flow

1. **Connector:** retrieves data using documented provider interfaces and declares individual supported capabilities. The initial Loyverse transport is GET-only and yields raw dictionaries for its allowlisted resources. Its current normalization surface is deliberately narrower than its raw read surface: variant input can map to canonical `product` records and receipt input can map to canonical `sale` records. Other readable resources are not implicitly canonical entities, and no canonical Loyverse activity mapper exists.
2. **Raw store (planned):** retains a source payload securely, with strict access controls and retention rules. Raw payloads must never be committed here.
3. **Normalizer:** maps only supported source fields into canonical records; unknowns remain unknown. Generic canonical contracts and CSV normalization exist, while the experimental Loyverse path currently implements only the product and sale mappings described above. Additional Loyverse mappings remain unsupported until their source semantics are sufficient and tested.
4. **Validator (available):** validates canonical JSON records using the versioned schema.
5. **Consumer:** reads records with explicit source provenance and version metadata.

The public fixtures are synthetic. The optional `source.raw_ref` is a non-sensitive reference to a raw payload, **not** a guarantee that storage has been implemented.

### RAW/provenance security boundary

Raw retention is **not implemented in v0.1**. A future implementation must treat source payloads as potentially containing credentials, personal data and other provider-sensitive fields even when the canonical record does not expose them.

- Retain raw payloads only when a documented normalization, audit or replay requirement justifies retention; collection alone is not a retention reason.
- Keep raw payloads outside canonical records, logs, exceptions, public fixtures and repository history. Never place access tokens, authorization headers or other credentials in `source.raw_ref`.
- `source.raw_ref` is an opaque, non-sensitive locator. It must not contain an embedded payload, URL userinfo, query parameters or fragments carrying source data or credentials.
- Access to retained raw data must be narrower than access to normalized records, scoped to the relevant store/tenant, and auditable where a deployment supports auditing.
- Define a finite retention period before enabling raw storage. Expiry must delete the payload and may leave a non-sensitive provenance record; OpenRetailSchema v0.1 does not prescribe a universal duration because legal and operational requirements differ by deployment.
- Redaction must happen before raw content reaches application logs, diagnostics, fixtures or support bundles. Redaction is a defense against disclosure, not a substitute for retention limits or access control.
- A missing, expired or inaccessible raw payload must not invalidate an otherwise valid canonical record. Consumers must not require dereferencing `raw_ref` to interpret canonical fields.

The repository's fixture-safety regression tests provide a narrow public-repository guard for common sensitive field names and unsafe `raw_ref` forms. They do **not** certify arbitrary runtime payloads as free of personal data or secrets, and they do not constitute a runtime retention implementation.

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
