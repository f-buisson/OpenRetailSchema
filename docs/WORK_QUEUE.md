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
- `REWORK` — review found specific defects that must be corrected before new scope is opened.
- `BLOCKED` — progress requires a documented dependency, authorization or external condition.

Allowed transitions:

```
IDLE -> READY
READY -> BUILDING
BUILDING -> REVIEW
REVIEW -> ACCEPTED
REVIEW -> REWORK
REVIEW -> BLOCKED
REWORK -> BUILDING
BLOCKED -> READY
ACCEPTED -> READY
```

Do not skip `REVIEW` to mark implementation accepted.

## Concurrency rules

1. Record the observed HEAD before starting a transition.
2. Immediately before writing, refresh HEAD and this file.
3. If HEAD changed unexpectedly, re-evaluate the lot instead of overwriting newer work.
4. Only the phase responsible for the current transition may change the state.
5. A lot is not complete because code exists; completion requires reproducible evidence.
6. Cosmetic edits do not justify a state transition.
7. If a run ends after code changes but before evidence is complete, leave the state at `BUILDING` or `REVIEW` as appropriate and describe the missing evidence.
8. If the same blocker survives two consecutive planning passes, narrow the task or move to the next independent roadmap criterion while keeping the blocker documented.

## Current handoff

- Work ID: `UNASSIGNED`
- Roadmap phase: `UNASSIGNED`
- State: `IDLE`
- Observed base HEAD: `ceeabfa7be8d2c788a1e10f49e65461799e07b20`
- Produced HEAD: `-`
- Scope: `-`
- Acceptance criteria:
  - `-`
- Evidence required:
  - `-`
- Evidence produced:
  - `-`
- Review verdict: `-`
- Rework or blocker: `-`
- Next action: select the first incomplete acceptance criterion in the highest-priority roadmap phase after refreshing the repository.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file.
