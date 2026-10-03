# Loyverse reuse audit

[Roadmap](ROADMAP.md) · [POS integration registry](POS_INTEGRATIONS.md)

This note prevents duplicated Loyverse engineering across the F-Buisson retail projects.

## Rule

Before implementing a Loyverse P2/P3 item, first inspect the existing authorized evidence and implementations in the maintainer's other retail projects when access is available. Reuse already-established **behavior, constraints, edge cases and synthetic test ideas** instead of rediscovering them.

Do not copy private or non-Apache-2.0 source code into OpenRetailSchema unless its licensing and provenance explicitly permit that reuse. Port only the vendor-neutral behavior needed by this repository, with OpenRetailSchema-native code and tests.

External product evidence remains **external evidence**. It can justify what OpenRetailSchema should test, but it does not make the OpenRetailSchema connector live-tested or release-ready.

## Existing engineering to check before new work

### Alertarif

Existing work already covers or provides evidence for many Loyverse behaviors relevant to OpenRetailSchema:

- personal-token read access exercised against an authorized real account;
- catalog, variants, inventory, taxes, stores and merchant reads;
- receipt/sales experiments, including refunds;
- cursor pagination and the documented 250-page-size boundary;
- incremental reads using provider update timestamps;
- repeated imports without duplicate records;
- missing price/stock/tax values preserved as unknown instead of zero;
- merchant currency observed as an object containing a code;
- HTTP 402 history-entitlement behavior observed on a real account;
- 401/403/429/provider-failure classification and Retry-After-aware behavior in tests;
- outage/recovery and incremental catch-up scenarios;
- synthetic end-to-end regression scenarios.

These are inputs for OpenRetailSchema normalization and conformance tests. They are not OpenRetailSchema connector certification.

### PlanCaisse

Existing work already covers or provides evidence for:

- OAuth authorization/exchange/refresh flow design and synthetic tests;
- least-privilege read scopes;
- stores, employees and receipts integration behavior;
- cursor pagination;
- distinct handling for 401, 402, 403, 429 and provider failures;
- timezone confirmation where Loyverse returns UTC without a store timezone;
- partial-day completeness tracking;
- multi-store boundaries;
- token sealing/storage boundaries;
- refresh-token behavior and expiry handling.

The PlanCaisse integration matrix records extensive automated coverage. Its live OAuth path has remained dependent on vendor developer-portal access, so simulated OAuth evidence must not be relabeled as a successful live OAuth test.

## P2 reuse map

Before starting a new lot, classify the target as one of:

1. **Already implemented in OpenRetailSchema** — review and close the roadmap item if evidence is sufficient.
2. **Implemented elsewhere, not yet ported** — use the established semantics and edge cases, then implement the smallest Apache-2.0 OpenRetailSchema equivalent.
3. **Externally evidenced only** — convert the observation into synthetic regression coverage where useful, without claiming repository certification.
4. **Actually missing** — research and implement new behavior.

Known examples:

- Pagination already exists in OpenRetailSchema and has regression tests; do not implement a second pagination layer.
- Unknown-versus-zero behavior is already evidenced externally and is being normalized in OpenRetailSchema; preserve that semantic rather than redesigning it.
- Incremental checkpoints, 402 handling, rate-limit behavior and outage recovery already have substantial evidence in the other projects; inspect that evidence before creating new P2 lots.
- A live OpenRetailSchema connector test still requires OpenRetailSchema itself to call an authorized account. External product tests cannot close that gate.
- Personal-token evidence and OAuth evidence must remain separate.

## Handoff requirement

Any planner, builder or reviewer working on Loyverse should read this file before defining a new P2/P3 lot. The work description should state whether the behavior is new, already present in OpenRetailSchema, or being ported from established external evidence.

The goal is to avoid three independent Loyverse implementations drifting apart while keeping OpenRetailSchema vendor-neutral, reproducible and license-safe.
