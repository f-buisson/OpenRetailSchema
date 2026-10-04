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
- State: `BUILDING`
- Base product HEAD: `c7c623503fc1e33ef682116fcaedb9a3b0774341`.
- Observed start HEAD: `895ab27d8bb2eb1cab27f5485cff6a3f917d75ad`; its only change after the compatible product base was the Planner handoff in this file.
- Produced HEAD so far: `71caf91df4c44db243bb5d1216d13e668875dbe5`.
- Implemented: the existing GET path now has a finite 1..5-attempt policy (default 3); only connection failures, 429, and classified 5xx provider errors are retryable. 401/402/403 and other permanent failures remain immediate. `merchant()` and paginated collection reads share the same `_get()` path; no write operation or second transport was introduced. 429 can carry a short `Retry-After` delta capped at 5 seconds.
- Synthetic tests added: transient recovery, transient exhaustion preserving sanitized classification, 401/402/403 single-attempt behavior, bounded 429 delay, retry-attempt validation, and malformed/excessive Retry-After inputs.
- Evidence status: execution is not yet claimed. A fresh local checkout was attempted after the commits but the environment could not resolve `github.com`, so no targeted or regression result is recorded.
- Known pre-review correction: harden `_bounded_retry_after()` so non-finite numeric strings such as `nan`/`inf` are rejected before sleeping; the new synthetic test intentionally includes these cases. Then update the public capability documentation from “Not implemented” to synthetic-tested bounded GET retries.
- Acceptance criteria still pending: execute `python -m unittest tests.test_loyverse_retry -v`, then the full local suite from the exact corrected HEAD. Only after both are green should the lot move `BUILDING -> REVIEW`.
- Next executable action: make the finite-delay correction, align `docs/POS_INTEGRATIONS.md`/architecture if needed, run targeted + full regression when execution access is available, and record the exact Produced HEAD and evidence.
- Debt check: pagination and canonical mapping remain unchanged; no competing client or write retry path was added.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
