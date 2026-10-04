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
- State: `ACCEPTED`
- Observed main HEAD before verdict: `085bed86d22b443c4ad7be16b1d1341a2e2ec9b1` (coordination-only transition after evidence; no later product change).
- Produced HEAD: `e0dba9fec38f31a52c6b8ce163d430451dc94685`.
- Accepted behavior: `canonical_sale()` maps documented receipt identity, explicit timestamp/store/direction, opaque line/variant identity, quantity, line gross money and receipt tax while deliberately omitting vendor `total_money` from canonical `gross_total` because their semantics are not equivalent. Refund direction is carried by `sale_kind`; source signs are preserved rather than invented.
- Reproducible evidence: GitHub Actions run `37171006683` on evidence HEAD `53353f76257c2f0372121bd0a1d6609709855f78` completed successfully. Exact targeted command `python -m unittest tests.test_loyverse_sale -v` and full regression `python -m unittest discover -s tests -v` both passed. The evidence commit after Produced HEAD changes only the existing test workflow; later commits before review are coordination-only.
- Review checks: missing monetary values remain absent rather than zero; binary floats fail closed; SALE/REFUND is explicit; timestamps require the canonical offset-aware boundary; malformed receipt/store/kind/line identity fails closed; fixtures are synthetic; no secret, real payload, PII, proprietary code, OAuth, persistence, retry or checkpoint behavior is introduced.
- Roadmap effect: this bounded sale-normalization tranche is accepted, but the broader P2 criterion `Audit and normalize connectors/loyverse.py against the canonical contracts` remains incomplete until its remaining bounded normalization work is independently evidenced. No roadmap checkbox is changed by this verdict.
- Next action: Planner must immediately select another independent incomplete roadmap criterion or bounded sub-lot and transition `ACCEPTED -> READY`; do not wait for persistent storage, StoreLine access, or live connector evidence.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
