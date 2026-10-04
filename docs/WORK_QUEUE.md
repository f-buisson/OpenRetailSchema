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
- State: `REVIEW`
- Base product HEAD: `47a77543cbd05897b459b03a16e7dbc635b326ff`.
- Observed start HEAD: `4569fe83336ccbb2372cc0bbf5e5c206a247c8f3` (planner handoff only after the recorded product base).
- Produced HEAD: `fea2e8f3a368d77f27763820a82fdbcc3b2b5f9e`.
- Evidence: `docs/POS_INTEGRATIONS.md` declares the current Loyverse capability boundary: GET-only merchant and allowlisted raw collections, bounded pagination, canonical product + sale only, canonical activity and writes unsupported, retries/checkpoints unimplemented, and live connector/OAuth certification untested. `docs/ARCHITECTURE.md` now matches that boundary and no longer says the transport cannot output canonical records.
- Consistency check: compared the documentation against exact `connectors/loyverse.py` on main: `_COLLECTIONS` contains items/variants/inventory/taxes/stores/receipts/employees/pos_devices/shifts; `merchant()` is GET-only through the transport; `iter_collection()` provides bounded cursor pagination; `canonical_product()` and `canonical_sale()` are the only canonical Loyverse mappers. No activity mapper, write operation, retry loop or persistent checkpoint exists.
- Test evidence: no test execution is claimed for this documentation-only completion pass. No executable product code changed.
- Scope guard satisfied: no P3 capability manifest, parallel transport/mapping path, secret, real payload or unsupported inferred field was introduced.
- Review request: verify the documentation diff and capability/code consistency, then decide ACCEPTED or REWORK. The roadmap checkbox remains unchanged for the reviewer to accept with reproducible evidence.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
