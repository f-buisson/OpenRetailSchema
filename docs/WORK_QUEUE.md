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

- Work ID: `P2-LOYVERSE-CAPABILITIES-01`
- Roadmap phase: P2 — document explicit connector capabilities and unsupported fields/features
- State: `BUILDING`
- Base product HEAD: `47a77543cbd05897b459b03a16e7dbc635b326ff`.
- Observed start HEAD: `4569fe83336ccbb2372cc0bbf5e5c206a247c8f3` (planner handoff only after the recorded product base).
- Produced HEAD so far: `77695c196b81a708b91cb4d62124f8245fcfaf2e`.
- Progress: `docs/POS_INTEGRATIONS.md` now has one explicit Loyverse capability declaration. Manual comparison against exact `connectors/loyverse.py` confirms GET-only `merchant()`, raw `_COLLECTIONS` for items/variants/inventory/taxes/stores/receipts/employees/pos_devices/shifts, bounded cursor pagination, canonical product + sale only, no canonical activity, no writes, no retries and no persistent checkpoints. Evidence levels remain separated; live connector and OAuth certification are explicitly untested.
- Remaining acceptance work: correct the stale statements in `docs/ARCHITECTURE.md` so architecture reflects the accepted product/sale canonical mapping boundary. No regression result is claimed in this pass; no executable product code changed.
- Scope guard: do not introduce the P3 versioned capability-manifest abstraction early and do not add a parallel transport/mapping path.
- Next action: update `docs/ARCHITECTURE.md` only, re-check it against current connector symbols and capability declaration, then move `BUILDING -> REVIEW` with the documentation diff as evidence. Run the local regression suite if execution access permits; do not require heavy CI for this documentation-only lot.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
