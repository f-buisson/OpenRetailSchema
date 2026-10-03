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

- Work ID: `P1-FIXTURES-01`
- Roadmap phase: `P1 — Generic CSV import`
- State: `READY`
- Observed base HEAD: `69e1c7f2e1ff3995108a5a1d4976ee3c1be5c86d`
- Produced HEAD: `-`
- Scope: make the existing fabricated sales/activity CSV contract cases executable regression evidence for refunds, missing monetary values and DST boundaries. Reuse the accepted timestamp normalizer where appropriate; do not implement a full sales/activity importer, persistent storage, vendor behavior, or connector certification. PR #8 is a separate open fixture proposal: inspect it before editing overlapping fixture files and avoid duplicating or overwriting concurrent work.
- Acceptance criteria:
  - Regression tests load the committed fabricated sales/activity CSV fixtures rather than reproducing their rows only as inline literals.
  - The refund case proves the explicit negative source amount/sign is preserved as supplied; no vendor refund convention is inferred.
  - The missing monetary-value case proves an empty/absent source value remains missing and is never converted to numeric zero.
  - The DST activity case proves the two offset-bearing repeated wall times represent distinct absolute instants through the accepted timestamp normalization contract.
  - Any additional naive-local DST case taken from PR #8 must preserve the documented rule: nonexistent spring time and ambiguous fallback time without disambiguation are rejected. Do not duplicate those rows if PR #8 changes or lands first.
  - Tests are offline, deterministic and synthetic; existing regression suite remains green.
  - The roadmap fixture criterion is not marked complete by the Builder; review decides whether the evidence is sufficient.
- Evidence required:
  - Exact focused test command and passing output for the fixture regression tests.
  - Exact full regression command and passing output, locally when available or on the exact produced commit via the existing lightweight CI.
  - Diff limited to fixture regression tests and only fixture/documentation changes strictly necessary to close a demonstrated coverage gap.
  - No secrets, real POS/customer data, private code, co-author trailer, prohibited attribution, or unsupported vendor claims.
- Evidence produced: `-`
- Review verdict: `-`
- Rework or deferred dependency: `-`
- Next action: Builder should refresh `main` and this file, inspect open PR #8 for overlap, transition `P1-FIXTURES-01` from `READY` to `BUILDING`, then implement the smallest offline regression tests that exercise the committed refund, missing-value and DST fixture rows. Preserve the scope boundary: fixtures/contracts only, not a sales/activity importer.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
