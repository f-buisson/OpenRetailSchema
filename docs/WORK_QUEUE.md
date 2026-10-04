# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states:

- `IDLE` — no lot is currently assigned.
- `READY` — a scoped lot has acceptance criteria and may be implemented.
- `BUILDING` — implementation has started from the recorded base.
- `REVIEW` — implementation is complete enough to review.
- `ACCEPTED` — evidence satisfies the recorded acceptance criteria.
- `REWORK` — review found specific defects that must be corrected.
- `DEFERRED` — this specific lot cannot currently be completed because it depends on an external condition, authorization, live account, hardware, unavailable evidence or other dependency. DEFERRED never blocks the project.

Allowed transitions:

```
IDLE -> READY
READY -> BUILDING
BUILDING -> REVIEW
REVIEW -> ACCEPTED
REVIEW -> REWORK
REWORK -> BUILDING
REVIEW -> DEFERRED
DEFERRED -> READY
ACCEPTED -> READY
```

Do not skip `REVIEW` to mark implementation accepted.

## Non-blocking rule

The project must keep advancing while useful independent work exists.

1. A dependency may defer one lot, but it must never freeze the global queue.
2. When a lot becomes `DEFERRED`, record the exact dependency and the condition that would make that lot actionable again.
3. In the same reviewer/planner cycle when practical, move on to the next independent incomplete roadmap criterion and create a new `READY` lot.
4. If the first incomplete criterion of the highest-priority phase depends on unavailable external evidence, preserve that criterion as incomplete and work on the next independent criterion without falsely marking the deferred criterion complete.
5. Human access, vendor authorization, live credentials, external hardware or unavailable real data are reasons to defer that specific proof, not reasons to stop development, tests, documentation, adapters, fixtures or other independent roadmap work.

## Concurrency rules

1. Record the observed product HEAD before starting a transition.
2. Immediately before writing, refresh HEAD and this file.
3. A commit that only updates `docs/WORK_QUEUE.md` for coordination is an expected handoff change, not a product-base collision.
4. If product files changed unexpectedly, re-evaluate the lot instead of overwriting newer work.
5. Only the phase responsible for the current transition may change the state.
6. A lot is not complete because code exists; completion requires reproducible evidence.
7. Cosmetic edits do not justify a state transition.
8. If a run ends after code changes but before evidence is complete, leave the state at `BUILDING` or `REVIEW` as appropriate and describe the missing evidence.
9. Never leave the global workflow waiting on one unavailable dependency when another useful independent roadmap item can be worked.

## Current handoff

- Work ID: `P2-LOYVERSE-PRODUCT-01`
- Roadmap phase: P2 — audit and normalize `connectors/loyverse.py` against canonical contracts
- State: `READY`
- Observed main HEAD: `9953fd0f3da72d7d74992822663b787ff45e0436`
- Scope: add one canonical Loyverse product/variant normalization path using the already accepted `source_external_id()` and `canonical_money()` primitives; synthetic input only. Do not add a second transport, pagination path, money parser, identifier helper or vendor-data fallback.
- Reuse classification: OpenRetailSchema already owns the primitive ID/currency/decimal/money semantics; external Loyverse work supplies behavioral/test input only. This lot composes those existing primitives into the repository's canonical product contract with repository-native code.
- Acceptance criteria:
  - A synthetic Loyverse product/variant fixture with valid opaque source id and non-empty name maps deterministically to a schema-valid v0.1 `product` record with `source.provider = "loyverse"` and the exact source external id preserved.
  - Canonical `id` construction is deterministic and collision-safe for the mapped source identity; no random or inferred identifier is introduced.
  - A valid source price is emitted only through the existing `canonical_money()` path and uses validated merchant currency; explicit zero remains `0` while absent/null/unsupported price remains absent rather than becoming zero.
  - Missing/blank required identity or name fails closed with a stable sanitized error/result; malformed optional SKU/barcode values are not silently coerced.
  - Targeted tests cover happy path, missing-vs-zero price, malformed required identity/name and at least one malformed optional field.
  - The resulting record is exercised through the repository's canonical schema validator/conformance path, not only asserted as a Python dictionary.
  - Existing Loyverse tests and the relevant canonical contract regression tests pass locally; no full GitHub Actions run is required unless local evidence is unavailable or a reviewer needs independent proof.
  - Public capability documentation is not advanced beyond implemented behavior; if this lot exposes a new public mapping entry point, its supported/unsupported boundary is documented in the same lot.
- Required evidence: exact targeted test command/result, exact canonical validation/regression command/result, produced commit SHA, and confirmation that no real payload, token or private source code entered the repository.
- Rework or blocker: `-`
- Debt state: 0 open PRs at planning time; stale PRs #8-#12 were closed unmerged by the accepted consolidation lot. No critical TODO/FIXME was found in the default-branch code search. This lot reuses the single existing Loyverse normalization primitives instead of creating parallel helpers.
- Next action: Builder moves `READY -> BUILDING` from the latest compatible `main`, implements only this bounded synthetic product normalization slice and records reproducible evidence before REVIEW.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
