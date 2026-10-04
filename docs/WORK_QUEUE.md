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

- Work ID: `P2-LOYVERSE-NORM-AUDIT-01`
- Roadmap phase: P2 — audit and normalize `connectors/loyverse.py` against canonical contracts
- State: `BUILDING`
- Base product HEAD: `181bc1a532507d5ff2a4f2758ec841300a95d751`.
- Produced HEAD: `e0484bd9a9a5d5f62288693df9da9fc9ee1cc552`.
- Audit result: canonical emission is limited to `product` and `sale`. Existing tests validate both against v0.1, exercise malformed required inputs, and preserve missing/null != explicit zero while rejecting binary-float monetary coercion. No canonical `activity` mapper exists.
- Product change: `docs/POS_INTEGRATIONS.md` now states the exact canonical emission surface and explicitly keeps activity unsupported. Raw `shifts`/other readable collections are not treated as canonical mappings, and no shift/receipt/session inference is introduced.
- Evidence attempted: exact targeted command prepared for the four `canonical_product` tests plus `tests.test_loyverse_sale`, followed by `python -m unittest discover -s tests -v`. Local execution could not start because this runtime could not resolve `github.com` for a fresh checkout; no passing result is claimed. No commit status was published yet for Produced HEAD at the last check.
- Next action: obtain reproducible targeted and full-suite results against `e0484bd9a9a5d5f62288693df9da9fc9ee1cc552` (existing CI is acceptable if local checkout remains unavailable). If green, propose only the P2 normalization checkbox and transition `BUILDING -> REVIEW`; if red, correct only the demonstrated regression.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
