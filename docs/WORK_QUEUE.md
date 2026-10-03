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

- Work ID: `P2-LOYVERSE-NORM-03`
- Roadmap phase: `P2 — Loyverse reference connector`
- State: `REVIEW`
- Observed main HEAD: `149421056527863425b36c15f9e301dbc236fb3d`
- Produced HEAD: `b04610c143cc3ec4c95e05f3a2e9e28fbb7d05c8` on `main`; helper commit `2b446b1fe0236be162e12a692ce29371c9259973`, focused-test commit `b04610c143cc3ec4c95e05f3a2e9e28fbb7d05c8`.
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete until a real persistence boundary exists; do not invent storage only to close it.
- Reuse classification: OpenRetailSchema already has raw Loyverse transport plus bounded currency/numeric helpers; canonical source provenance requires a non-guessing source identifier boundary. External project evidence is design/test input only and does not certify this connector.
- Scope: add one small Loyverse source-identity normalization helper and focused synthetic tests. Accept an opaque vendor `id` only when it is a non-empty string; preserve its exact content rather than coercing, trimming into a different identifier, hashing, or synthesizing a replacement. Return/fail closed for missing, null, blank/whitespace-only, numeric, boolean or structured values. Keep this helper at the raw-to-canonical boundary; do not build full product/sale mappings, retries, checkpoints, tax inference, live calls or OAuth behavior in this lot.
- Acceptance criteria:
  - A focused helper in `connectors/loyverse.py` exposes a validated opaque source identifier suitable for canonical `source.external_id` without inventing missing data.
  - A valid non-empty string identifier is preserved byte-for-byte as a Python string, including meaningful surrounding characters; validation may reject whitespace-only but must not silently rewrite identifiers.
  - Missing/null, empty or whitespace-only strings, booleans, numbers, lists and objects fail closed and never become strings such as `"None"`, `"0"` or synthesized IDs.
  - Focused tests prove valid preservation and every rejected class above using fabricated data only.
  - Existing currency/numeric/pagination behavior remains unchanged and the full regression suite passes.
- Evidence required:
  - Exact product commit SHA and diff limited to the bounded helper/tests plus necessary coordination.
  - Exact focused test command and passing output.
  - Exact full regression command and passing output, locally or through one justified lightweight CI run on the exact product commit.
  - Confirmation that no secret, token, real payload, customer data, private code, co-author trailer or unsupported live/certification claim was introduced.
- Rework or deferred dependency: `-`
- Evidence: compare `ebcd6b1..b04610c` changes only `connectors/loyverse.py`, `tests/test_loyverse.py` and coordination. `source_external_id()` preserves valid opaque strings unchanged and rejects missing/null/blank, booleans, numeric and structured values. Existing lightweight CI run `37140272492` targets exact Produced HEAD `b04610c143cc3ec4c95e05f3a2e9e28fbb7d05c8` and completed successfully; its regression step is `python -m unittest discover -s tests -v`.
- Limits: this lot does not complete the roadmap-wide Loyverse normalization criterion and does not establish live/OAuth evidence.
- Next action: reviewer must certify the exact Produced HEAD and transition this Work ID to `ACCEPTED`, `REWORK` or `DEFERRED`; do not leave it in REVIEW for another cycle.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
