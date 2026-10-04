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

- Work ID: `P2-LOYVERSE-RETRY-01`
- Roadmap phase: P2 — implement bounded retries/error classification without unsafe retry of non-idempotent operations
- State: `ACCEPTED`
- Base product HEAD: `c7c623503fc1e33ef682116fcaedb9a3b0774341`.
- Produced HEAD: `01a3544b8af39f91146a51edc361a00d8cb8e0a4`.
- Accepted behavior: the only transport path is GET-only and uses a finite 1..5-attempt budget (default 3). Only connection failures, HTTP 429 and classified provider 5xx errors are retryable; 401/402/403 and other permanent failures remain immediate.
- Retry-After boundary: only finite numeric deltas in the inclusive 0..5-second range are accepted; malformed, negative, excessive, `nan` and `inf` values are ignored before sleeping.
- Safety: no write/non-idempotent transport exists, pagination and canonical mappings are unchanged, errors remain sanitized, and no secret or real payload was introduced by this lot.
- Reproducible evidence: GitHub Actions run `37188662229` completed successfully on exact Produced HEAD `01a3544b8af39f91146a51edc361a00d8cb8e0a4`; checkout and dependency installation passed, followed by the existing targeted Loyverse sale test and the complete `python -m unittest discover -s tests -v` regression suite, which discovers `tests/test_loyverse_retry.py`.
- Review verdict: `ACCEPTED`. The synthetic retry tests directly cover recovery, exhaustion, permanent-access single-attempt behavior, bounded 429 delay, retry-attempt validation, and malformed/non-finite/excessive Retry-After values. A second dedicated retry-only workflow step is not required because the exact Produced HEAD is already covered by reproducible full-suite CI and the retry test module is part of discovery.
- Evidence boundary: synthetic/repository certification only. No live Loyverse request or OAuth behavior is claimed.
- Planner handoff: transition `ACCEPTED -> READY` immediately on the next independent incomplete P2 criterion. Incremental checkpoints and sanitized/synthetic end-to-end mappings can proceed without waiting for live credentials; live connector and OAuth evidence remain separate criteria.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
