# Roadmap

[Home](../README.md)

The roadmap defines **acceptance criteria and execution order**, not completion dates. Work should progress in small, reviewable lots. A feature is only marked delivered after reproducible evidence exists in this repository.

OpenRetailSchema is infrastructure for downstream products, not a reason to delay their release. Until the first retail products are commercially stable, the project prioritizes work that removes duplicated POS engineering, produces a usable public release, or directly strengthens the Loyverse -> future Square connector path.

## Status vocabulary

- **Documented** — supported by current public vendor documentation.
- **Synthetic-tested** — exercised with fabricated fixtures in this repository.
- **Externally tested** — observed in an authorized test outside this repository; this is evidence, not connector certification.
- **Live-tested** — exercised by the OpenRetailSchema connector against an authorized test account.
- **Release-ready** — local regression tests pass from a fresh checkout and documentation matches the tested behavior.
- **Deferred** — incomplete by design because a concrete dependency does not exist yet; it must not be reported as delivered.

External evidence must never be presented as OpenRetailSchema connector certification.

## Execution order

Use **WIP = 1** for implementation lots. Work on the first incomplete, independent acceptance criterion in the highest-priority phase, unless a smaller release blocker below it prevents immediate adoption. A documented external dependency may be deferred without freezing unrelated work.

Do not invent infrastructure merely to close a checkbox. In particular, storage-only behavior does not justify introducing persistent storage before a real consumer requires it.

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
- [ ] **Deferred until persistent storage exists:** define repeated-import/idempotency behavior and test it against the actual storage implementation.

The deferred storage criterion **does not block v0.1**. It becomes active only when the repository gains a real persistent store or a downstream consumer demonstrates a concrete persistence contract that belongs here.

**Exit gate:** product import is release-ready and the next CSV record types have explicit, non-guessing contracts.

### P1.5 — Publish v0.1

Goal: stop keeping a usable foundation permanently in “pre-release” state while unrelated connector work continues.

- [x] Run the complete local regression suite from a fresh checkout of the exact release HEAD.
- [x] Verify README installation/validation/import examples from that checkout.
- [x] Verify release contents contain no secrets, private fixtures, customer data or proprietary source.
- [x] Confirm `docs/COMPATIBILITY.md`, `docs/ARCHITECTURE.md` and CSV documentation match the release behavior.
- [x] Prepare concise release notes with explicit experimental boundaries.
- [x] Tag and publish **v0.1.0** — release tag points to `f26b34395396448e3a458c3a3e3b062172fb1661`, certified locally with 71/71 tests plus validator/CSV/security smoke checks.

**Release evidence (2026-10-05):** the pre-release fresh checkout of `a6eb30b` passed 71/71 local tests and the validator/CSV/security checks. After documentation alignment and PR #14 merge, the exact tagged SHA `f26b34395396448e3a458c3a3e3b062172fb1661` was re-tested: 71/71 tests passed, validator smoke passed for product, sale and activity fixtures, the documented synthetic product CSV import produced 3 canonical products with 0 rejected rows, and the tracked secret-pattern scan returned no matches.

**Exit gate:** an independent developer can clone/tag v0.1.0, validate canonical data and exercise the documented CSV path without project-specific knowledge.

### P2 — Loyverse reference connector

Goal: turn the experimental reader into the first evidence-backed reference POS connector and remove duplicated Loyverse engineering from downstream retail products.

**Reuse first:** before opening a new Loyverse lot, read [the cross-project reuse audit](LOYVERSE_REUSE.md). Existing behavior and evidence from the maintainer's other retail projects should be reused as design/test input rather than rediscovered. Private or non-Apache source code must not be copied into this repository without compatible provenance.

- [x] Review official Loyverse API documentation.
- [x] Record authorized external personal-token test findings separately from repository certification.
- [x] Implement an experimental read-only transport with injected synthetic-response tests.
- [x] Audit and normalize `connectors/loyverse.py` against the canonical contracts.
- [x] Document explicit connector capabilities and unsupported fields/features.
- [x] Implement and test pagination.
- [x] Implement bounded retries/error classification without unsafe retry of non-idempotent operations.
- [x] Implement incremental checkpoints without converting missing values to zero.
- [x] Exercise sanitized/synthetic end-to-end mappings — PR #15 covers paginated products, sales/refunds, schema validation, unknown-vs-zero semantics, checkpoint resume and failed traversal; local 74/74 tests and the PR CI passed before merge.
- [x] Run the full suite from a fresh checkout.
- [ ] Perform an authorized live OpenRetailSchema connector test; record only non-sensitive evidence.
- [ ] Keep personal-token validation distinct from OAuth; do not claim OAuth until independently tested.

**Exit gate:** the connector is live-tested, its capability declaration matches observed behavior, and no secret or real payload is committed.

### P3 — Connector contract

Goal: make additional POS integrations predictable without forcing every consumer to understand vendor-specific behavior.

- [x] Define a versioned connector capability manifest — PR #16 introduced the vendor-neutral manifest with explicit supported/unsupported declarations and unknown-by-absence semantics; local 78/78 tests passed and PR CI completed successfully before merge.
- [x] Define common read operations and explicit unsupported-operation behavior — `connectors.operations` exposes the finite read surface and distinguishes unsupported from undeclared operations; reusable contract tests cover both fail-closed paths.
- [x] Define pagination, checkpoint, rate-limit and error semantics — `docs/CONNECTOR_EXECUTION.md` separates ephemeral cursors from caller-owned durable checkpoints and fixes stable retry/error classes.
- [x] Define provenance/RAW boundaries and redaction requirements — `docs/ARCHITECTURE.md` requires source provenance, finite RAW retention where used, secret/PII exclusion and redaction before diagnostics or publication.
- [x] Use the normalized Loyverse connector as the first reference implementation — the adapter implements the common read contract and its capability manifest is exercised by the same reusable harness.
- [x] Add connector conformance tests reusable by future adapters — `tests/connector_conformance.py` is adapter-agnostic and `tests/test_loyverse_contract.py` proves the Loyverse implementation against it.

**P3 evidence (2026-10-06):** commits `6522824` through `9a82a38` define the execution contract, implement the common Loyverse adapter and apply the reusable conformance harness. This closes the generic connector-contract work without changing the still-open P2 live-provider/OAuth gates.

**Exit gate:** a third-party developer can implement a connector from public documentation and run the same conformance tests.

### P4 — Square next, then evidence-backed adapters

Goal: expand only where official documentation and testable access justify implementation, with **Square as the next commercial priority after the Loyverse reference path is stable**.

- [x] Maintain `docs/POS_INTEGRATIONS.md` as the evidence registry.
- [x] Keep the community POS documentation/synthetic-mapping request open.
- [x] Re-check current official Square documentation, scopes, pagination, webhooks/rate limits and access requirements — completed on 2026-10-06. The first transport foundation landed before this full review; that sequencing debt is recorded rather than hidden, and the merged surface was re-checked against the current official material.
- [x] Select the minimum Square read-only surface needed by downstream retail products — `stores.read`, `products.read`, `sales.read` and `inventory.read` are the bounded synthetic surface.
- [x] Reuse the P3 conformance contract rather than creating Square-specific abstractions — the Square adapter is exercised by the same reusable connector harness as Loyverse.
- [x] Normalize completed Square sales into canonical sale records without guessing money, tax or event-time semantics — completed orders use `closed_at`; line variation identity and quantity are preserved; monetary fields remain absent until currency-exponent conversion is explicit.
- [x] Normalize unambiguous Square returns/refunds by linking PaymentRefund.order_id to the refund order: PaymentRefund.created_at supplies occurrence time and OrderReturnLineItem supplies itemization; ambiguous multi-refund allocation fails closed and money remains absent.
- [ ] Perform an authorized Square Sandbox or seller-account connector run and keep that evidence distinct from OAuth/Marketplace certification.
- [ ] Periodically verify official public documentation for Shopify, Lightspeed, Clover, Odoo, Epos Now and other relevant systems. **2026-10-06:** Shopify reviewed against current official GraphQL Admin documentation; adapter remains deferred until POS-origin semantics and authorized access are sufficiently evidenced. Other listed systems still require this review cycle.
- [x] Record capabilities, scopes, pagination, quotas/rate limits and plan restrictions only when supported by current official sources — `docs/SQUARE.md` records the four minimum read scopes, cursor behavior, generic 429/backoff guidance, Sandbox/production separation, webhook boundaries, and explicitly avoids inventing a numeric quota or endpoint-specific paid-plan requirement.
- [ ] Invite third-party contributions of official links, synthetic fixtures and fabricated CSV examples — never secrets, confidential documentation or real customer exports.
- [ ] Select later adapters only after evidence quality, access and maintenance cost are sufficient.
- [ ] StoreLine remains deferred until the exact NCR Voyix/StoreLine interface and authorization are established; documented CSV remains an acceptable interim path.

**P4 evidence (2026-10-06):** PR #21 established the transport-injected Square read foundation on the shared connector contract; PR #23 added bounded read-only rate-limit retries; PR #24 added conservative canonical product normalization and merged after its exact HEAD passed the public test workflow. Live Square, OAuth and Marketplace certification remain explicitly unclaimed. PR #29 subsequently locked Square GET/POST pagination page-budget safety into synthetic regression coverage. The 2026-10-06 Shopify documentation review records cursor pagination, cost-based throttling, the default 60-day order-history boundary and the unresolved POS-origin mapping without starting an adapter.

**Exit gate:** every advertised adapter has a capability declaration and evidence level; unsupported or untested behavior is explicit.

### P5 — Adoption and stable evolution

Goal: make the project safe and useful for independent consumers without creating speculative infrastructure.

- [ ] Complete useful French translations while keeping English canonical.
- [ ] Review contribution provenance and Apache-2.0 compatibility for accepted contributions.
- [ ] Publish migration guarantees and a versioning policy suitable for 1.0 planning.
- [ ] Add an SDK only when repeated consumer code demonstrates a stable need.
- [ ] Add a service API only when a real deployment use case justifies operational complexity.
- [ ] Define the 1.0 gate only after v0.1 adoption and at least one live-tested reference connector provide evidence for stable contracts.

## Commercialization-support rule

When two useful tasks are available, prefer the one that does one of the following:

1. removes duplicated connector work from Alertarif, PlanCaisse or PlanFlux;
2. closes a reproducible blocker to v0.1;
3. advances the Loyverse reference connector toward live-tested status;
4. strengthens the generic connector contract needed by the next Square adapter;
5. fixes a correctness, security or provenance defect.

Do **not** spend a cycle on speculative SDKs, service hosting, cosmetic documentation expansion or another POS adapter while one of those five classes of work is available.

## Hourly maintenance rule

Each maintenance pass should:

1. Re-read repository HEAD, recent commits, open issues/PRs and the relevant roadmap phase. For Loyverse P2/P3 work, also read `docs/LOYVERSE_REUSE.md` before defining a new lot.
2. Preserve WIP = 1 for implementation work and finish/review the active lot before opening another.
3. Prefer one small verifiable change over broad cosmetic edits.
4. Run available local tests when execution access permits; never claim an unexecuted test passed.
5. Update this roadmap only for real state changes.
6. Keep `docs/POS_INTEGRATIONS.md`, useful French documentation and the community POS issue aligned when integration evidence changes.
7. Never publish secrets, tokens, private customer data, proprietary code or confidential artifacts.
8. Use GitHub Actions/CI moderately and only when it provides useful evidence or unblocks a roadmap/release step; prefer targeted existing jobs and avoid repetitive or heavy runs.
9. Never force-push. Commit metadata must contain no co-author trailer or prohibited attribution.
10. If blocked by access, authorization or a required human test, document the exact blocker and continue independent work.
11. At the 20:00 Europe/Paris pass, report only real changes, commits, evidence, tests actually executed, limits, risks, external contributions, next priorities and required human actions.

## Non-goals for the first release

Real-time prediction, POS price writes, workforce optimization, vendor-specific private APIs, production hosting and speculative SDK/service layers are not required for a useful interoperable starting point.
