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
- State: `ACCEPTED`
- Observed main HEAD before verdict: `4e546e9d99544674a40c664298e2908e3da3775d` (review handoff only after evidence HEAD)
- Produced HEAD: `974c769bd4ada236fb5e9dddaeb68bb001c40794`
- Scope certified: one canonical Loyverse product/variant normalization path using the accepted `source_external_id()` and `canonical_money()` primitives with synthetic input only.
- Acceptance evidence:
  - `canonical_product()` emits deterministic schema-valid product records and preserves source provenance.
  - Required identity/name and malformed non-null SKU/barcode fail closed with stable sanitized codes.
  - Absent/null/unsupported price remains absent while explicit numeric zero remains zero; no missing value is converted to zero.
  - Existing Tests run `37167760956` succeeded on evidence HEAD `ee53a9966ca0a4f953f6bf27a9e9c3d05ce65c38`; its targeted four-test product-normalization step and full regression step both succeeded.
  - Produced HEAD to evidence HEAD changed only `.github/workflows/tests.yml` and `docs/WORK_QUEUE.md`; no product or product-test implementation changed concurrently.
  - Tests use fabricated literals only; no credential, real payload, customer data or external/private source code is part of this lot.
- Limits: this verdict certifies only the bounded product/variant normalization tranche. It does not complete the global P2 normalization criterion, claim a live connector test, OAuth support or unsupported-field coverage beyond this scope.
- Rework or blocker: none for this lot.
- Next action: Planner should immediately transition `ACCEPTED -> READY` with the next independent bounded incomplete roadmap lot. Persistent-storage idempotency and unavailable live/vendor evidence must not hold the queue.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
