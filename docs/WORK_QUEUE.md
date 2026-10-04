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

- Work ID: `P2-LOYVERSE-CAPABILITIES-01`
- Roadmap phase: P2 — document explicit connector capabilities and unsupported fields/features
- State: `BUILDING`
- Base product HEAD: `47a77543cbd05897b459b03a16e7dbc635b326ff`.
- Observed start HEAD: `4569fe83336ccbb2372cc0bbf5e5c206a247c8f3` (planner handoff only after the recorded product base).
- Scope: make the public Loyverse capability declaration match the implementation already on `main`; correct the stale architecture statement that says the transport does not emit canonical records. Do not introduce the P3 versioned capability-manifest abstraction early and do not add a parallel transport/mapping path.
- Acceptance criteria:
  1. `docs/POS_INTEGRATIONS.md` has one explicit Loyverse capability matrix/declaration separating raw readable resources from canonical emission, and marks unsupported/unimplemented behavior without implying live certification.
  2. The declaration matches `connectors/loyverse.py`: GET-only merchant plus the currently allowlisted collections; pagination is supported; canonical emission is product + sale only; activity and write operations are unsupported; retries, checkpoints and OAuth certification remain unimplemented/untested as applicable.
  3. `docs/ARCHITECTURE.md` no longer contradicts accepted behavior: it describes the current product/sale canonical mapping boundary without claiming raw collections are canonical entities.
  4. Evidence levels remain explicit: repository behavior is synthetic-tested; external personal-token observations remain external evidence; no live OpenRetailSchema or OAuth claim is introduced.
  5. No secret, real payload, private code, vendor-confidential material or inferred unsupported field is added. No new helper/manifest/compatibility layer is created for documentation-only capability facts.
  6. A targeted consistency check (manual diff against `_COLLECTIONS`, `merchant()`, `canonical_product()` and `canonical_sale()` is sufficient) is recorded, and the existing local regression suite is run if the environment permits; no heavy CI is required for documentation-only changes.
- Required evidence: changed-file diff showing the capability declaration and architecture correction; explicit comparison to current connector symbols/resources; regression result if actually executed. Do not claim an unexecuted test.
- Debt check: 0 open PRs. No duplicate capability implementation exists. Immediate debt found: `docs/ARCHITECTURE.md` still says the Loyverse transport does not output canonical records, contradicting the accepted product/sale mappers and current POS registry. This lot fixes that contradiction while completing the next P2 criterion and deliberately avoids creating the future P3 manifest early.
- Next action: update only the capability/architecture documentation needed to reflect current code, verify it against exact `main`, then supply recorded evidence for review.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
