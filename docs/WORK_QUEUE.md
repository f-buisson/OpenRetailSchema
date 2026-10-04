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
- State: `REVIEW`
- Base product HEAD: `c7c623503fc1e33ef682116fcaedb9a3b0774341`.
- Observed start HEAD: `895ab27d8bb2eb1cab27f5485cff6a3f917d75ad`; its only change after the compatible product base was the Planner handoff in this file.
- Produced HEAD: `01a3544b8af39f91146a51edc361a00d8cb8e0a4`.
- Implemented: the single existing GET path has a finite 1..5-attempt policy (default 3). Only connection failures, HTTP 429, and classified provider 5xx errors are retryable. 401/402/403 and other permanent failures remain immediate. `merchant()` and paginated collection reads share `_get()`; no write operation or second transport exists.
- Retry-After hardening: only finite numeric deltas in the inclusive 0..5-second range are accepted. `nan`, `inf`, malformed, negative and excessive values are ignored before any sleep.
- Synthetic coverage: transient recovery, exhaustion preserving sanitized classification, 401/402/403 single-attempt behavior, bounded 429 delay, attempt validation, and malformed/non-finite/excessive Retry-After inputs.
- Documentation: `docs/POS_INTEGRATIONS.md` now advertises bounded retries as GET-only, synthetic-tested and not live-certified; checkpoint and live/OAuth boundaries remain explicit.
- Evidence: GitHub Actions run `37188662229` on exact Produced HEAD `01a3544b8af39f91146a51edc361a00d8cb8e0a4` completed successfully. The workflow checked out that HEAD, installed the declared dev requirements, passed its targeted Loyverse sale step, then passed `python -m unittest discover -s tests -v`; the discovery suite includes `tests/test_loyverse_retry.py`. The immediately preceding run `37188648300` on functional correction HEAD `9250168498ae5f81e6e310672f995a0d80d0b5c7` also passed the full discovery suite.
- Evidence boundary: no live Loyverse request was made and no local fresh-checkout result is claimed. The repository CI provides reproducible fresh-checkout regression evidence for the exact Produced HEAD; live certification remains a separate P2 criterion.
- Review focus: verify the finite retry classification/delay policy, confirm no unsafe/non-idempotent retry path was introduced, and decide whether the existing full discovery proof is sufficient for this lot or whether a dedicated retry-only workflow step is required before acceptance.
- Debt check: pagination and canonical mapping remain unchanged; no competing client or write retry path was added.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
