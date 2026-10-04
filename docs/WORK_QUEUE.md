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

- Work ID: `P2-LOYVERSE-SALE-01`
- Roadmap phase: P2 — audit and normalize `connectors/loyverse.py` against canonical contracts
- State: `READY`
- Observed main HEAD: `180ad60cb9a1ac27374372304de5e420c6c9d414`
- Reuse classification: receipt/refund behavior is externally evidenced in the maintainer's other retail work but is not yet normalized in OpenRetailSchema. Use those established semantics and synthetic test ideas only; do not copy private/non-Apache source or claim external evidence as repository certification.
- Scope: add one bounded canonical Loyverse receipt-to-sale normalization path using existing canonical primitives where applicable. Use fabricated receipt dictionaries only. Do not add transport, pagination, retry, checkpoint, OAuth or persistence behavior in this lot.
- Acceptance criteria:
  - A single canonical sale normalizer maps a fabricated, documented-compatible receipt shape to a v0.1 `sale` record with deterministic Loyverse provenance and validates against `schemas/v0.1/record.schema.json`.
  - Required receipt identity, store identity, event timestamp and at least one valid line fail closed with stable sanitized error codes when absent or malformed; no identifier or timestamp is invented.
  - Sale versus refund classification and quantity/amount signs follow only semantics supported by current public Loyverse documentation plus the already-recorded external receipt/refund evidence; ambiguous vendor fields are omitted or rejected rather than guessed.
  - Monetary fields reuse the existing decimal/currency path; absent/null monetary values remain absent and explicit numeric zero remains zero. Binary floats, booleans and unsupported source values are not silently coerced.
  - Line provenance/product references remain opaque and deterministic; missing product identity is not replaced with a fabricated product.
  - Targeted synthetic tests cover a schema-valid sale, a refund/sign boundary, missing-versus-zero money, and at least one malformed required identity/time/line case.
  - The affected public canonical contract has no regression: run the targeted tests and the existing local full regression suite, recording exact commands and results. CI is not required unless local evidence is unavailable or insufficient.
  - No token, real payload, customer/employee data, private source code or confidential artifact enters the repository.
- Required evidence: produced commit SHA; exact targeted-test command/result; exact full-regression command/result; schema-validation proof from the repository validator/test path; concise statement of which receipt semantics came from public documentation versus external authorized evidence versus synthetic fixtures.
- Debt check: 0 open PRs at planning time; no competing receipt normalizer was found on `main`; the accepted product normalizer already owns product mapping and must not be duplicated. P1 persistent-storage idempotency remains intentionally incomplete until storage exists. No critical TODO/FIXME or branch overlap was identified that should precede this bounded lot.
- Next action: Builder should refresh `main`, confirm this coordination-only handoff is the only change after the observed HEAD, transition `READY -> BUILDING`, then implement only this bounded receipt normalization and its tests.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
