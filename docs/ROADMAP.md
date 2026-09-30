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

- [ ] Define a declarative CSV column-mapping contract with explicit required fields.
- [ ] Handle encodings, field separators, decimal and date formats without guessing.
- [ ] Emit provenance-rich canonical records and actionable row-level errors.
- [ ] Validate duplicate imports, bad rows, missing fields, partial totals and timezones.
- [ ] Document a fully reproducible local import.

## Loyverse

- [x] Review official Loyverse API documentation and existing real-account token test findings (separate product; see the [integration registry](POS_INTEGRATIONS.md)).
- [ ] Independently implement and validate a read-only token client in this repository, using synthetic fixtures first.
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
- [ ] More POS adapters proposed with evidence and maintainers. The public [integration registry](POS_INTEGRATIONS.md) includes official documentation leads.

## Non-goals for the first release

Real-time prediction, POS price writes, workforce optimization, vendor-specific private APIs, and production hosting are not required for a useful interoperable starting point.
