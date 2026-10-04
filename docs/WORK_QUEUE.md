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
- State: `READY`
- Base product HEAD: `c7c623503fc1e33ef682116fcaedb9a3b0774341`.
- Reuse classification: implemented/evidenced in the maintainer's other retail projects, not yet ported to OpenRetailSchema. Reuse the established 401/402/403/429/provider-failure and Retry-After edge cases as design/test input only; do not copy private source or treat external evidence as connector certification.
- Scope: extend the single existing Loyverse GET transport path with one bounded retry policy. Do not create a parallel transport/client. Keep all currently exposed operations read-only. Retry only transient failures that are safe for GET; authentication/authorization/plan errors and other permanent client failures must fail immediately. Preserve sanitized errors and never expose token, query secrets or provider response bodies.
- Acceptance criteria:
  1. Synthetic targeted tests prove a transient GET failure can recover within a finite configured/default attempt bound and that exhaustion returns a stable sanitized `LoyverseError` classification.
  2. Synthetic negative tests prove 401, 402 and 403 are not retried; existing explicit classifications remain intact. 429 handling is bounded and honors a valid bounded `Retry-After` signal if the implementation exposes response metadata; malformed/excessive delay input must not create an unbounded wait.
  3. No non-idempotent/write retry path is introduced. The connector remains GET-only and uses one canonical transport/retry implementation.
  4. Existing pagination, canonical product/sale, missing-versus-zero and public contract tests remain green. Retry behavior must not invent records, checkpoints, amounts or missing values.
  5. Public capability/architecture documentation is updated in the same lot if retry support changes an advertised capability; documentation must distinguish synthetic-tested behavior from live certification.
- Required evidence: targeted retry/error tests including recovery, exhaustion and permanent-error no-retry cases; then the local regression suite. Do not launch heavy CI unless local execution cannot provide the required proof or a repository gate specifically requires it.
- Next executable action: Builder refreshes `main`, transitions this Work ID `READY -> BUILDING`, inspects the existing transport/tests first, then implements the smallest retry change satisfying the criteria without adding a second client or transport abstraction.
- Debt check: 0 open PRs at planning time; no TODO/FIXME search hits; no existing retry implementation found on `main`; pagination and canonical mapping already exist and are explicitly out of scope. This lot does not add a competing path.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
