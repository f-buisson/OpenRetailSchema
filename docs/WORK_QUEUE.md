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

- Work ID: `DEBT-PR-CONSOLIDATE-01`
- Roadmap phase: cross-phase consolidation before further P2 expansion
- State: `ACCEPTED`
- Observed main HEAD: `5ab65387e489da3a9a36b5ffbac0cc47d9ab702f`
- Produced HEAD: `d76f5619b70e612d07384ac05716e0ba037e9eed` (coordination-only BUILDING handoff; no product behavior changed in this lot)
- Scope: bounded stale-PR consolidation only; no product behavior changes.
- Acceptance criteria:
  - PRs #8-#12 are explicitly classified against current `main`.
  - Fully covered/superseded PRs are closed without merging obsolete code.
  - Any retained PR must serve a concrete incomplete roadmap criterion.
  - No accepted behavior is removed, no force-push occurs, and no compatibility helper is introduced.
  - Roadmap completion is not reopened without evidence.
- Review evidence:
  - Refreshed `main`, `docs/ROADMAP.md`, this handoff, and the PR queue before verdict.
  - PRs #8, #9, #10, #11 and #12 are all closed and unmerged; the repository has no open pull request at review time.
  - #8 is unique fixture material but belongs to already completed P1 DST/fixture scope and does not serve the remaining persistent-storage idempotency criterion.
  - #9 is superseded by the accepted timestamp-normalization path on `main`; merging its competing API would create an unnecessary compatibility path.
  - #10 contains partially unique executable fixture checks, but those checks cover refund, missing-value and DST semantics already owned by completed P0/P1 criteria and do not serve an incomplete criterion.
  - #11 and #12 are superseded by accepted Loyverse currency and numeric normalization behavior already present on `main`.
  - `docs/ROADMAP.md` remains unchanged and correctly keeps P1 persistent-storage idempotency plus the broader P2 connector criteria incomplete.
  - The Produced HEAD and the later REVIEW handoff changed only `docs/WORK_QUEUE.md`; no product behavior was modified by this consolidation.
  - No additional CI run was justified for this coordination-only lot.
- Rework or blocker: `-`
- Next action: Planner must move `ACCEPTED -> READY` by selecting the next bounded independent incomplete roadmap criterion. Do not wait on P1 persistent-storage idempotency or future live/vendor evidence when independent P2 work remains available.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
