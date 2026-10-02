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
REWORK -> BUILDING
REVIEW -> BLOCKED
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

- Work ID: `P1-TIME-01`
- Roadmap phase: `P1 — Generic CSV import`
- State: `READY`
- Observed base HEAD: `e41a0152f8b014c6059a390c6acf0cb4b4a66364`
- Produced HEAD: `-`
- Scope: make the documented sales/activity timestamp mapping executable with one small vendor-neutral normalization helper and focused tests; do not implement the sales/activity importer yet. PR #8 remains a separate synthetic-fixture change and must not be represented as importer certification.
- Acceptance criteria:
  - An input timestamp that already carries `Z` or an explicit UTC offset is accepted without timezone inference and represents the same absolute instant after normalization.
  - A naive local timestamp is accepted only with an explicit IANA timezone and, when the local wall time is repeated, an explicit occurrence/offset disambiguation.
  - `2026-03-29T02:15` in `Europe/Paris` is rejected as nonexistent; ambiguous `2026-10-25T02:15` without disambiguation is rejected; both valid fall-back occurrences can be distinguished.
  - Focused tests prove these cases without network access, vendor assumptions, real data, or silent timezone inference.
  - Existing local regression suite remains green; the roadmap criterion stays unchecked until review confirms the executable contract is sufficient.
- Evidence required:
  - Exact local test commands and passing output for the focused timestamp tests and existing regression suite.
  - Diff limited to the normalization helper, focused tests, and only documentation strictly required to keep behavior aligned.
  - No secrets, private code/data, co-author trailer, or prohibited attribution in the produced commit metadata/content.
- Evidence produced:
  - `-`
- Review verdict: `-`
- Rework or blocker: `-`
- Next action: Builder refreshes `main` and this file, transitions `READY -> BUILDING`, implements `P1-TIME-01` on a small dedicated branch, runs the required local tests, records the produced HEAD/evidence, then hands the same Work ID to review without opening new scope.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file.
