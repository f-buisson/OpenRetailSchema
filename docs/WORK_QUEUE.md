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
- State: `REVIEW`
- Observed main HEAD: `ee53a9966ca0a4f953f6bf27a9e9c3d05ce65c38`
- Produced HEAD: `974c769bd4ada236fb5e9dddaeb68bb001c40794` (product normalization plus targeted tests)
- Scope: add one canonical Loyverse product/variant normalization path using the already accepted `source_external_id()` and `canonical_money()` primitives; synthetic input only. Do not add a second transport, pagination path, money parser, identifier helper or vendor-data fallback.
- Implemented:
  - `canonical_product()` composes the accepted opaque-id and money primitives into a deterministic `loyverse:variant:<external_id>` canonical product without transport or parent-item inference.
  - Required source id/name fail closed with stable sanitized codes; malformed non-null SKU/barcode fail closed rather than being coerced.
  - Price is omitted for absent/null/unsupported values and explicit numeric zero is preserved through `canonical_money()`.
  - Fabricated tests cover deterministic/schema-valid output, missing-vs-zero price, invalid required fields and malformed optional fields; schema validation uses the repository v0.1 Draft 2020-12 schema directly.
- Evidence available:
  - Existing Tests run `37167760956` completed successfully on `ee53a9966ca0a4f953f6bf27a9e9c3d05ce65c38`.
  - Its targeted step executed the four `canonical_product` tests successfully, followed by a successful full `python -m unittest discover -s tests -v` regression step.
  - Comparing Produced HEAD to the evidence HEAD shows only `.github/workflows/tests.yml` and this coordination file changed; no product or test implementation changed after the Produced HEAD.
  - No real payload, credential, customer data or external/private source code is used by the product-normalization tests; their records are fabricated literals.
- Rework or blocker: none identified in the bounded lot.
- Next action: reviewer must decide `REVIEW -> ACCEPTED`, `REVIEW -> REWORK` or `REVIEW -> DEFERRED` from the recorded evidence. If accepted, the Planner should immediately open the next independent incomplete roadmap lot.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
