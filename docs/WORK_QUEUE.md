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

- Work ID: `P2-LOYVERSE-SALE-01`
- Roadmap phase: P2 — audit and normalize `connectors/loyverse.py` against canonical contracts
- State: `REVIEW`
- Observed main HEAD: `de571c1cf6d2c04c14117249710bf961e851c944` (the commits after Produced HEAD only change the existing test workflow and this coordination file; no later product file changed).
- Produced HEAD: `e0dba9fec38f31a52c6b8ce163d430451dc94685`.
- Implemented: `canonical_sale()` maps documented receipt identity, `receipt_date`, store, SALE/REFUND direction, opaque line/variant identity, quantity, line `gross_total_money`, and receipt `total_tax`. It deliberately omits vendor `total_money` because public Loyverse documentation defines that value as paid/returned money including discounts, taxes, surcharges and tips, which is not safely equivalent to canonical `gross_total`.
- Sign rule: public Loyverse documentation defines `receipt_type` as SALE/REFUND and describes refund `total_money` as money returned; repository compatibility rules require preserving source signs rather than inventing negation. Synthetic refund coverage therefore keeps positive quantity/line money positive and carries direction in `sale_kind`.
- Synthetic evidence: schema validation/determinism, refund sign boundary, missing-vs-zero line money plus binary-float rejection, and fail-closed receipt/store/time/kind/line validation with stable codes. Fixtures are fabricated literals only.
- Reproducible evidence: GitHub Actions run `37171006683` on evidence HEAD `53353f76257c2f0372121bd0a1d6609709855f78` completed successfully. The job passed exact targeted command `python -m unittest tests.test_loyverse_sale -v` and then full regression `python -m unittest discover -s tests -v`. Evidence HEAD differs from Produced HEAD only by the existing test workflow; product code and tests are unchanged.
- Scope limits: no transport, pagination, retry, checkpoint, OAuth, persistence, real payload, token, customer/employee data or private source code was added. External authorized receipt/refund observations remain external evidence only; all repository tests are synthetic.
- Reviewer action: inspect Produced HEAD, canonical contracts and the exact green evidence; issue `ACCEPTED`, `REWORK` or `DEFERRED` without creating new scope.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
