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
- State: `READY`
- Observed main HEAD: `43ad54a4142650b0b3b0b682f55f22e3e1fb6d95`
- Trigger: the last Loyverse normalization lot is accepted, but five older PRs (#8, #9, #10, #11, #12) remain open. Main already contains the accepted Loyverse currency/numeric behavior represented by #11/#12, and P1 timestamp/fixture criteria are marked complete. Opening another P2 code lot before classifying this queue would risk duplicate or competing paths.
- Scope: perform a bounded stale-PR consolidation. Compare PRs #8-#12 against current `main`, classify each as still useful, fully superseded by `main`, partially superseded, or unsafe to merge. Close only PRs whose intended behavior is already present or deliberately replaced on `main`; do not merge stale code merely to empty the queue. If a PR contains a unique still-required change, leave it open and record the exact missing behavior and the roadmap criterion it serves. Do not modify product behavior in this lot.
- Acceptance criteria:
  - PRs #8, #9, #10, #11 and #12 are each compared against current `main` and receive an explicit evidence-based classification.
  - Any PR fully covered or superseded by `main` is closed without merging obsolete code.
  - Any PR left open has one concrete non-duplicated purpose tied to an incomplete roadmap criterion.
  - No accepted P0/P1/P2 behavior is removed, no branch is force-pushed, and no new compatibility path/helper is introduced.
  - `docs/ROADMAP.md` is changed only if the comparison reveals a factual mismatch; completed criteria are not reopened or rechecked without evidence.
  - After cleanup, the remaining open-PR queue is short and non-overlapping enough that the next P2 lot can be selected without ambiguity.
- Evidence required:
  - Before/after list of relevant open PR numbers and states.
  - For every closed PR, a concise pointer to the equivalent/replacement behavior on `main` or the accepted roadmap evidence that makes the PR obsolete.
  - For every retained PR, the exact unique diff/behavior still absent from `main` and its roadmap owner.
  - Confirmation that this consolidation introduced no product code, secret, private data, proprietary source, force-push or unsupported certification claim.
- Debt snapshot: 5 relevant open PRs observed (#8-#12). #11/#12 visibly overlap behavior already present on `main`; #8-#10 concern P1 work whose corresponding roadmap criteria are already marked complete and therefore require classification before any merge. No critical product defect was found in the accepted Loyverse money helper. This lot reduces branch/PR ambiguity rather than adding another implementation path.
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete until a real persistence boundary exists; do not invent storage only to close it.
- Next action: Builder moves `READY -> BUILDING`, refreshes `main` and all five PR heads, performs the comparison/classification, closes only proven-obsolete PRs, records evidence, then hands the same Work ID to REVIEW. No heavy CI is required unless the comparison exposes a product change that genuinely needs proof.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
