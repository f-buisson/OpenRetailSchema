# Roadmap

[Home](../README.md)

The roadmap defines **acceptance criteria and execution order**, not completion dates. Work should progress in small, reviewable lots. A feature is only marked delivered after reproducible evidence exists in this repository.

## Status vocabulary

- **Documented** — supported by current public vendor documentation.
- **Synthetic-tested** — exercised with fabricated fixtures in this repository.
- **Externally tested** — observed in an authorized test outside this repository; this is evidence, not connector certification.
- **Live-tested** — exercised by the OpenRetailSchema connector against an authorized test account.
- **Release-ready** — local regression tests pass from a fresh checkout and documentation matches the tested behavior.

External evidence must never be presented as OpenRetailSchema connector certification.

## Execution order

Work on the first incomplete acceptance criterion in the highest-priority phase unless a blocker is documented. Independent research and documentation may continue in parallel, but must not displace contract and regression-test work.

### P0 — Canonical contract hardening — v0.1 foundation

Goal: make the canonical model safe enough that downstream applications can rely on its semantics.

- [x] English canonical overview and French introduction.
- [x] Initial vendor-neutral record schema: sales, products and aggregated activity.
- [x] Synthetic valid and invalid fixtures.
- [x] Offline JSON Schema validator and local regression tests.
- [x] Document pre-1.0 compatibility rules.
- [x] Reject canonical event timestamps that omit an explicit UTC offset.
- [x] Compare activity interval ordering by absolute instant, including a DST fallback fixture.
- [x] Lock the DST fallback and reversed-interval fixtures into automated regression tests.
- [x] Add explicit fixtures/tests proving **unknown or absent tax != 0% tax**.
- [x] Add refund/return fixtures and define sign/quantity semantics without guessing vendor conventions.
- [x] Add incomplete-price fixtures proving **absent != zero** for monetary values.
- [x] Verify currency-object rules, including unsupported/mismatched currency behavior.
- [x] Review RAW/provenance retention rules for secret, PII and payload leakage risks.
- [x] Publish the Apache 2.0 license with owner approval.
- [x] Publish a POS evidence registry and safe issue form for external connector proposals.

**Exit gate:** all P0 fixtures are covered by reproducible local tests; compatibility and security documentation match actual validator behavior.

### P1 — Generic CSV import

Goal: provide a vendor-neutral fallback path that does not guess missing business data.

- [x] Define an explicit, versioned CSV mapping for product records, with source provenance and deterministic IDs.
- [x] Handle explicit UTF-8 encodings, field separators and decimal separators without guessing.
- [x] Emit schema-validated canonical product records and sanitized, row-numbered rejection codes.
- [x] Detect duplicate product IDs, bad rows and missing fields; reject incomplete imports by default.
- [x] Document a reproducible local product import with fabricated CSV and mapping examples.
- [x] Execute the CSV regression tests from a fresh checkout of the exact public repository.
- [x] Define sales/activity date, timezone and UTC-offset mapping.
- [x] Add sales/activity CSV fixtures covering refunds, missing values and DST boundaries.
- [ ] Define repeated-import/idempotency behavior and test it against persistent storage only when storage is introduced.

**Exit gate:** product import is release-ready and the next CSV record types have explicit, non-guessing contracts.

### P2 — Loyverse reference connector

Goal: turn the experimental reader into the first evidence-backed reference POS connector.

**Reuse first:** before opening a new Loyverse lot, read [the cross-project reuse audit](LOYVERSE_REUSE.md). Existing behavior and evidence from the maintainer's other retail projects should be reused as design/test input rather than rediscovered. Private or non-Apache source code must not be copied into this repository without compatible provenance.

- [x] Review official Loyverse API documentation.
- [x] Record authorized external personal-token test findings separately from repository certification.
- [x] Implement an experimental read-only transport with injected synthetic-response tests.
- [x] Audit and normalize `connectors/loyverse.py` against the canonical contracts.
- [ ] Document explicit connector capabilities and unsupported fields/features.
- [x] Implement and test pagination.
- [x] Implement bounded retries/error classification without unsafe retry of non-idempotent operations.
- [ ] Implement incremental checkpoints without converting missing values to zero.
- [ ] Exercise sanitized/synthetic end-to-end mappings.
- [ ] Run the full suite from a fresh checkout.
- [ ] Perform an authorized live OpenRetailSchema connector test; record only non-sensitive evidence.
- [ ] Keep personal-token validation distinct from OAuth; do not claim OAuth until independently tested.

**Exit gate:** the connector is live-tested, its capability declaration matches observed behavior, and no secret or real payload is committed.

### P3 — Connector contract

Goal: make additional POS integrations predictable without forcing every consumer to understand vendor-specific behavior.

- [ ] Define a versioned connector capability manifest.
- [ ] Define common read operations and explicit unsupported-operation behavior.
- [ ] Define pagination, checkpoint, rate-limit and error semantics.
- [ ] Define provenance/RAW boundaries and redaction requirements.
- [ ] Use the normalized Loyverse connector as the first reference implementation.
- [ ] Add connector conformance tests reusable by future adapters.

**Exit gate:** a third-party developer can implement a connector from public documentation and run the same conformance tests.

### P4 — POS evidence and additional adapters

Goal: expand only where official documentation and testable access justify implementation.

- [x] Maintain `docs/POS_INTEGRATIONS.md` as the evidence registry.
- [x] Keep the community POS documentation/synthetic-mapping request open.
- [ ] Periodically verify official public documentation for Square, Shopify, Lightspeed, Clover, Odoo, Epos Now and other relevant systems.
- [ ] Record capabilities, scopes, pagination, quotas/rate limits and plan restrictions only when supported by current official sources.
- [ ] Invite third-party contributions of official links, synthetic fixtures and fabricated CSV examples — never secrets, confidential documentation or real customer exports.
- [ ] Select the next adapter only after evidence quality, access and maintenance cost are sufficient.
- [ ] StoreLine remains blocked until the exact NCR Voyix/StoreLine interface and authorization are established; documented CSV remains an acceptable interim path.

**Exit gate:** every advertised adapter has a capability declaration and evidence level; unsupported or untested behavior is explicit.

### P5 — Adoption and stable release

Goal: make the project safe and useful for independent consumers.

- [ ] Complete useful French translations while keeping English canonical.
- [ ] Review contribution provenance and Apache-2.0 compatibility for accepted contributions.
- [ ] Publish migration guarantees and a versioning policy suitable for 1.0 planning.
- [ ] Add an SDK only when repeated consumer code demonstrates a stable need.
- [ ] Add a service API only when a real deployment use case justifies operational complexity.
- [ ] Prepare and tag v0.1 only after P0 and the product-CSV release gate pass.

## Hourly maintenance rule

Each maintenance pass should:

1. Re-read repository HEAD, recent commits, open issues/PRs and the relevant roadmap phase. For Loyverse P2/P3 work, also read `docs/LOYVERSE_REUSE.md` before defining a new lot.
2. Prefer one small verifiable change over broad cosmetic edits.
3. Run available local tests when execution access permits; never claim an unexecuted test passed.
4. Update this roadmap only for real state changes.
5. Keep `docs/POS_INTEGRATIONS.md`, useful French documentation and the community POS issue aligned when integration evidence changes.
6. Never publish secrets, tokens, private customer data, proprietary code or confidential artifacts.
7. Use GitHub Actions/CI moderately and only when it provides useful evidence or unblocks a roadmap step; prefer targeted existing jobs and avoid repetitive or heavy runs.
8. Never force-push. Commit metadata must contain no co-author trailer or prohibited attribution.
9. If blocked by access, authorization or a required human test, document the exact blocker and continue independent work.
10. At the 20:00 Europe/Paris pass, report only real changes, commits, evidence, tests actually executed, limits, risks, external contributions, next priorities and required human actions.

## Non-goals for the first release

Real-time prediction, POS price writes, workforce optimization, vendor-specific private APIs, production hosting and speculative SDK/service layers are not required for a useful interoperable starting point.
