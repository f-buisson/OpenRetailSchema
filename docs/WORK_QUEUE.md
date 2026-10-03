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

- Work ID: `P2-LOYVERSE-NORM-02`
- Roadmap phase: `P2 — Loyverse reference connector`
- State: `ACCEPTED`
- Observed review HEAD: `1e509eea4745e0abc53cf5ade4ace36286e7fd34`
- Produced HEAD: `357be67696f3ffaee47c52535a1f77ae7e439833` on `builder/P2-LOYVERSE-NORM-02` (PR #12), based on `20b5e95eac870a799dbc963c9b4fca612cbf3e63`.
- Scope reviewed: bounded synthetic normalization of Loyverse product/variant monetary and stock-like numeric source values, preserving unknown/null separately from explicit zero and failing closed for unsupported shapes.
- Evidence: PR #12 changes only `connectors/loyverse.py` and `tests/test_loyverse.py`; `source_decimal()` accepts finite `Decimal` and exact integers, preserves zero and precision, and rejects booleans, binary floats, strings, non-finite decimals and structured values. Exact produced-commit GitHub Actions run `37125933104` passed `python -m unittest discover -s tests -v` on `357be67696f3ffaee47c52535a1f77ae7e439833`.
- Concurrency review: current `main` advanced after the produced base through documentation/coordination work (`docs/WORK_QUEUE.md`, `docs/ROADMAP.md`, `docs/LOYVERSE_REUSE.md`). No later product-file change on `main` supersedes the reviewed connector/test diff. PR #12 currently requires integration with the newer base before merge; acceptance certifies the bounded product diff, not a merge result.
- Review verdict: `ACCEPTED` — all recorded criteria for this bounded lot are satisfied by reproducible synthetic evidence. The connector-wide roadmap criterion remains incomplete; this lot does not certify live behavior, OAuth, taxes, identifiers, provenance, persistence or the full canonical mapping.
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete until a real persistence boundary exists; do not invent storage only to close it.
- Rework or deferred dependency: `-`
- Next action: Planner should immediately select the next independent incomplete roadmap criterion and create a new `READY` lot. Before any further Loyverse P2/P3 lot, use `docs/LOYVERSE_REUSE.md` as required design/evidence input. Do not treat this acceptance as connector-wide or live certification.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
