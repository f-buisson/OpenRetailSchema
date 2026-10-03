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

- Work ID: `P2-LOYVERSE-NORM-02-INTEGRATE`
- Roadmap phase: `P2 — Loyverse reference connector`
- State: `ACCEPTED`
- Observed main HEAD: `3c70d1a76fe8a82d4f5caf6c5467f95b3d282b28`
- Produced HEAD: `8c63c4f34621616dcf285b1ea8fa45b82e932c77` on `main`; connector behavior commit `f0889aeca8b6d5739b261172d2be169a9231b846` followed by focused-test commit `8c63c4f34621616dcf285b1ea8fa45b82e932c77`.
- Source work: accepted `P2-LOYVERSE-NORM-02`, produced at `357be67696f3ffaee47c52535a1f77ae7e439833` in PR #12. The accepted `connectors/loyverse.py` and `tests/test_loyverse.py` content is now present on refreshed `main` without semantic expansion.
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete until a real persistence boundary exists; do not invent storage only to close it.
- Scope: integrate the already accepted bounded Loyverse numeric-normalization product diff onto current `main` without semantic expansion. Preserve current documentation/coordination changes and the accepted `source_decimal()` plus focused tests. Do not add new normalization behavior, live calls, OAuth claims, retries, checkpoints, tax inference, persistence or broad mapping in this lot.
- Acceptance criteria:
  - Current `main` receives the accepted `source_decimal()` behavior and its focused synthetic tests with no loss of newer main changes.
  - Missing/null remain unknown, explicit zero remains zero, finite `Decimal` and exact integers retain the accepted semantics, and unsupported/coercive shapes remain fail-closed exactly as reviewed.
  - The integration diff contains no unrelated product changes and does not alter the connector-wide roadmap completion claim.
  - Focused Loyverse tests and the full regression suite pass on the exact integrated commit.
  - PR #12 is either updated/merged cleanly or superseded by an equivalently reviewable integration path; no force-push is used.
- Evidence required:
  - Exact integrated commit SHA and comparison showing the accepted connector/test behavior is present on top of current `main`.
  - Exact focused test command and passing output.
  - Exact full regression command and passing output, locally or via the existing lightweight CI on the exact integrated commit.
  - Confirmation that no secret, token, real payload, customer data, private code, co-author trailer or unsupported certification claim was introduced.
- Rework or deferred dependency: `-`
- Evidence: direct content comparison against accepted HEAD `357be67696f3ffaee47c52535a1f77ae7e439833` shows identical accepted blobs for `connectors/loyverse.py` (`af2fe63a...`) and `tests/test_loyverse.py` (`79a3c5fc...`) on integrated `main`. Existing lightweight CI run `37133216430` completed successfully on exact Produced HEAD `8c63c4f34621616dcf285b1ea8fa45b82e932c77`. Its Ubuntu job installed `requirements-dev.txt` and successfully ran the full regression command `python -m unittest discover -s tests -v`. Review confirmed the integration diff from `3c70d1a...` is limited to the accepted connector behavior, its focused tests and coordination, and that later commits through `6d0ca33b...` only change coordination. No additional semantic change was introduced.
- Limits: no local pass is claimed because the earlier runtime could not resolve github.com. No live/OAuth behavior or connector-wide certification is claimed; this evidence is synthetic repository regression evidence only. The roadmap-wide Loyverse normalization criterion remains incomplete.
- Next action: Planner must immediately select the next independent incomplete roadmap criterion and create a bounded `READY` lot. The deferred P1 persistence-dependent idempotency criterion remains incomplete and must not hold the queue.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
