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

- Work ID: `P2-LOYVERSE-NORM-02`
- Roadmap phase: `P2 — Loyverse reference connector`
- State: `BUILDING`
- Observed base HEAD: `20b5e95eac870a799dbc963c9b4fca612cbf3e63`
- Produced HEAD: `357be67696f3ffaee47c52535a1f77ae7e439833` on `builder/P2-LOYVERSE-NORM-02` (PR #12).
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete until a real persistence boundary exists; do not invent storage only to close it.
- Scope: continue the incomplete Loyverse normalization audit with one synthetic product-value boundary. Add a small normalization helper or equivalent tested boundary for Loyverse product/variant monetary and stock values that preserves source absence/null as unknown rather than zero. Keep raw transport dictionaries separate from canonical records. Do not add live calls, OAuth claims, pagination changes, persistence, receipts, tax inference, or broad product mapping.
- Acceptance criteria:
  - Synthetic cases prove missing and explicit null price/stock inputs remain unknown (`None`/omitted as appropriate) and are never converted to numeric zero.
  - Explicit numeric zero remains distinguishable from missing/null and is preserved as zero when the source shape is otherwise valid.
  - Accepted numeric values preserve decimal precision; booleans, NaN/infinity, malformed strings and unsupported shapes fail closed instead of being guessed or coerced.
  - The implementation remains a normalization boundary only; it must not fabricate canonical currency, tax, identifiers or provenance fields that the source slice cannot prove.
  - Tests are offline, deterministic and synthetic, and the existing regression suite remains green.
  - The roadmap Loyverse normalization criterion remains incomplete unless review finds the connector-wide audit sufficient; this lot alone must not claim live connector or OAuth certification.
- Evidence required:
  - Focused tests showing absent/null != zero and explicit zero behavior for both monetary and stock-like values.
  - Exact focused test command and passing output.
  - Exact full regression command and passing output, locally when available or on the exact produced commit via existing lightweight CI when useful.
  - Diff limited to the Loyverse connector, focused tests, and minimal documentation only if needed to state a demonstrated boundary.
  - No network access, token, real payload, customer data, private code, co-author trailer, prohibited attribution, or unsupported vendor claim.
- Evidence produced:
  - PR #12 changes only `connectors/loyverse.py` and `tests/test_loyverse.py` at produced HEAD `357be67696f3ffaee47c52535a1f77ae7e439833`.
  - `source_decimal()` preserves missing/null as `None`, explicit integer/Decimal zero as zero, exact integer conversion and finite Decimal precision; booleans, binary floats, strings, non-finite Decimal values and structured values fail closed to `None`.
  - Focused synthetic tests cover both `price` and `in_stock` unknown-versus-zero behavior, high Decimal precision and unsupported shapes without network access.
  - No local execution is claimed in this environment. At the latest check, no GitHub Actions run had yet been published for the exact produced HEAD, so regression execution proof remains pending.
- Review verdict: `-`
- Rework or deferred dependency: `-`
- Next action: Builder should check CI for exact produced HEAD `357be67696f3ffaee47c52535a1f77ae7e439833`; if the existing full regression suite is green, record that exact run and transition this same Work ID to `REVIEW`; if it fails, correct only the demonstrated regression and keep the scope bounded.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
