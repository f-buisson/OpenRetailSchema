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
- State: `REVIEW`
- Observed main HEAD: `81811701efbae819ed37efa651f51411ce1f89f7`
- Produced HEAD: `d76f5619b70e612d07384ac05716e0ba037e9eed` (coordination-only BUILDING handoff; no product behavior changed in this lot)
- Trigger: five older PRs (#8-#12) remained open after their roadmap ownership had either been completed or superseded on `main`.
- Scope: bounded stale-PR consolidation only; no product behavior changes.
- Acceptance criteria:
  - PRs #8-#12 are explicitly classified against current `main`.
  - Fully covered/superseded PRs are closed without merging obsolete code.
  - Any retained PR must serve a concrete incomplete roadmap criterion.
  - No accepted behavior is removed, no force-push occurs, and no compatibility helper is introduced.
  - Roadmap completion is not reopened without evidence.
- Evidence:
  - Refreshed `main`, `docs/ROADMAP.md`, this handoff, and PR heads before cleanup.
  - #8: unique proposed naive-local DST CSV fixture, but its stated P1 ownership is already complete on the roadmap. It does not serve the sole remaining P1 criterion (persistent-storage idempotency), so retaining or merging it would reopen completed scope without evidence. Closed unmerged.
  - #9: superseded/unsafe to merge. Accepted `main` already owns timestamp normalization through `importers/time_normalization.py` and tests; #9 proposes a competing API/convention. Closed unmerged.
  - #10: partially unique test file, but every behavior it asserts (refund sign, absent monetary values, offset-bearing fallback semantics) belongs to P0/P1 criteria already marked complete. It does not serve the remaining P1 idempotency criterion or an incomplete P2 criterion. Closed unmerged rather than reopening completed scope.
  - #11: fully superseded by accepted Loyverse merchant-currency normalization on `main`. Closed unmerged.
  - #12: fully superseded by accepted Loyverse numeric normalization on `main`. Closed unmerged.
  - Before cleanup: five open stale PRs in this bounded set. After cleanup: zero open PRs from #8-#12; no overlapping retained purpose remains.
  - `docs/ROADMAP.md` was not changed: comparison found no factual mismatch requiring completed criteria to be reopened.
  - No product code, secret, private/customer data, proprietary source, force-push, new helper, CI run, or certification claim was introduced.
- Rework or blocker: `-`
- Next action: Reviewer verifies the five classifications and closed/unmerged state, then decides ACCEPTED or REWORK. Builder must not select a new scope from REVIEW.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
