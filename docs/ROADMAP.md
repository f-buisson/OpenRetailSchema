# Roadmap

[Home](../README.md)

The roadmap defines **acceptance criteria**, not completion dates. Features are only marked delivered after reproducible tests.

## Foundation — v0.1 (in progress)

- [x] English canonical overview and French introduction.
- [x] Initial vendor-neutral record schema: sales, products and aggregated activity.
- [x] Synthetic valid and invalid fixtures.
- [x] Offline JSON Schema validator and local regression tests.
- [ ] Document schema compatibility rules and add targeted edge-case fixtures (tax ambiguity, returns, incomplete prices, timezone offsets).
- [x] Publish the Apache 2.0 license with owner approval.
- [x] Publish a POS evidence registry and safe issue form for external connector proposals.
- [ ] Release/tag v0.1 once acceptance tests pass.

## Generic CSV import

- [x] Define an explicit, versioned CSV mapping for **product** records, with source provenance and deterministic IDs.
- [x] Handle explicit UTF-8 encodings, field separators and decimal separators for product imports, without guessing.
- [ ] Define date/timezone mapping for subsequent sales and activity imports.
- [x] Emit schema-validated canonical product records and sanitized, row-numbered rejection codes.
- [x] Detect duplicate product IDs within a file, bad rows and missing fields; reject incomplete imports by default.
- [ ] Test repeated imports against persistent storage; handle partial sales totals and timezone/DST edges in future sales imports.
- [x] Document a [reproducible local product import](CSV_IMPORT.md), including fabricated CSV and mapping examples.
- [ ] Execute the nine new CSV regression tests against a fresh checkout of the exact GitHub repository before calling the feature release-ready.

## Loyverse

- [x] Review official Loyverse API documentation and existing real-account token test findings (separate product; see the [integration registry](POS_INTEGRATIONS.md)).
- [x] Implement an experimental read-only Loyverse transport with injected synthetic-response regression tests.
- [ ] Execute the full regression suite and independently validate the OpenRetailSchema transport on an authorized live test account (separate-product tests do not count).
- [ ] Document actual read capabilities and unsupported features.
- [ ] Implement read-only pagination, safe retries and incremental checkpoints.
- [ ] Validate authorized synthetic or sanitized test data end to end.
- [ ] Report verified capabilities only; do not imply a certified integration prematurely.

## StoreLine

- [ ] Establish exactly which NCR Voyix / StoreLine interface is available and authorized.
- [ ] Obtain appropriate integration documentation and explicit capability scope.
- [ ] Implement only tested interfaces; allow CSV as an interim documented path.

## Adoption

- [ ] Versioned connector interface and reference connector.
- [ ] Public architecture and migration guarantees.
- [ ] Optional service API and client SDKs based on demonstrated consumer demand.
- [x] Open a community [POS documentation and synthetic-mapping request](https://github.com/f-buisson/OpenRetailSchema/issues/1).
- [ ] Deliver other POS adapters backed by evidence and maintainers. The public [integration registry](POS_INTEGRATIONS.md) includes official documentation leads.

## Non-goals for the first release

Real-time prediction, POS price writes, workforce optimization, vendor-specific private APIs, and production hosting are not required for a useful interoperable starting point.
