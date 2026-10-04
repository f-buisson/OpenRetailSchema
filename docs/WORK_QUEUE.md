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

- Work ID: `P2-LOYVERSE-CHECKPOINT-01`
- Roadmap phase: P2 — implement incremental checkpoints without converting missing values to zero
- State: `BUILDING`
- Base product HEAD: `5867ee4438ad74d26652318df26bd3de3f9f4e7b`.
- Builder base: `f3642e2f4f13a77773b9e7ee51a9d03544c16f19`; intervening changes were documentation/planning only and compatible with this lot.
- Reuse classification: implemented elsewhere, not yet ported. Alertarif provides external evidence for provider-update-time incremental reads, repeated imports without duplicates and outage catch-up; use those semantics and edge cases as design/test input only. Do not copy private/non-Apache source and do not relabel external evidence as OpenRetailSchema certification.
- Scope: add one canonical incremental-checkpoint path to the existing read-only Loyverse connector. A checkpoint must represent source progress explicitly, remain distinct from pagination cursors, be caller-supplied/returned rather than silently persisted, and advance only from valid source update information after successful processing. Do not introduce a second transport, storage layer, write path or speculative generic P3 abstraction.
- Acceptance: synthetic tests prove an initial sync without a checkpoint, resume from a valid checkpoint, deterministic monotonic advancement, repeated/resumed reads without inventing duplicate progress, and no checkpoint advancement when traversal/normalization fails.
- Acceptance: missing/null/invalid source update values remain unknown or rejected according to the narrow connector contract; they must never become numeric zero, epoch zero or a fabricated timestamp. Boundary tests must cover malformed timestamps and explicit UTC-offset handling where timestamps are used.
- Acceptance: pagination cursors remain ephemeral transport state and are never persisted/reused as incremental checkpoints. Existing pagination, retry, product and sale contracts remain regression-safe.
- Acceptance: document the exact checkpoint semantics and evidence level in `docs/POS_INTEGRATIONS.md` (and architecture documentation only if the public architecture contract changes). Do not claim live certification, OAuth behavior or persistent-storage idempotency.
- Evidence required: targeted checkpoint tests plus the complete local regression suite on the exact Produced HEAD. CI is optional and should be used only if local execution cannot provide reproducible proof or a fresh-checkout proof is deliberately needed.
- Next action: implement the connector-native update-time checkpoint path and synthetic tests, then run targeted and full local regressions before REVIEW.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
