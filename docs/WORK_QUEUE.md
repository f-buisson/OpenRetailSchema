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
- State: `BUILDING`
- Observed main HEAD: `801e2787880cc42bb06a4f21c64e38679e46bb4e` (READY handoff only; product base was compatible)
- Produced HEAD: `974c769bd4ada236fb5e9dddaeb68bb001c40794` (product normalization plus targeted tests)
- Scope: add one canonical Loyverse product/variant normalization path using the already accepted `source_external_id()` and `canonical_money()` primitives; synthetic input only. Do not add a second transport, pagination path, money parser, identifier helper or vendor-data fallback.
- Implemented:
  - `canonical_product()` composes the accepted opaque-id and money primitives into a deterministic `loyverse:variant:<external_id>` canonical product without transport or parent-item inference.
  - Required source id/name fail closed with stable sanitized codes; malformed non-null SKU/barcode fail closed rather than being coerced.
  - Price is omitted for absent/null/unsupported values and explicit numeric zero is preserved through `canonical_money()`.
  - Fabricated tests cover deterministic/schema-valid output, missing-vs-zero price, invalid required fields and malformed optional fields; schema validation uses the repository v0.1 Draft 2020-12 schema directly.
- Evidence available:
  - Repository HEAD was refreshed immediately before the progress handoff and remained the produced test commit; no concurrent product change was observed.
  - No real payload, credential, customer data or external/private source code was used; all new test records are fabricated literals.
  - No workflow run was published yet for Produced HEAD when checked, so no execution result is claimed.
- Rework or blocker: this execution environment has repository API/write access but no local checkout runner. Exact targeted and regression execution evidence is therefore still missing; this is an execution-proof limitation, not a product-data dependency.
- Next action: execute `python -m unittest tests.test_loyverse.LoyverseTests.test_canonical_product_is_schema_valid_and_deterministic tests.test_loyverse.LoyverseTests.test_canonical_product_keeps_missing_price_distinct_from_zero tests.test_loyverse.LoyverseTests.test_canonical_product_rejects_invalid_required_fields tests.test_loyverse.LoyverseTests.test_canonical_product_rejects_malformed_optional_fields` and `python -m unittest discover -s tests -v` against Produced HEAD. If both are green, record the exact results and move `BUILDING -> REVIEW`; if not, correct only the demonstrated regression.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
