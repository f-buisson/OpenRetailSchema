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

- Work ID: `P2-LOYVERSE-NORM-01`
- Roadmap phase: `P2 — Loyverse reference connector`
- State: `ACCEPTED`
- Observed base HEAD: `addec2106678b108b27aede2526dd3b9e862e950`
- Produced HEAD: `61ebc90497532e8e8dbc66d26049adc3f016a825` on `builder/P2-LOYVERSE-NORM-01` (PR #11).
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete because the roadmap explicitly requires testing it against persistent storage only when storage is introduced. Resume that criterion when a repository persistence boundary exists; do not invent storage merely to close P1.
- Scope: audit the experimental `connectors/loyverse.py` boundary against the canonical contracts and implement one small synthetic normalization slice for merchant currency only. Keep transport/raw dictionaries separate from canonical records. Do not add live calls, OAuth claims, pagination changes, persistence, product/sales mapping, or vendor behavior not supported by repository evidence.
- Acceptance criteria:
  - Existing `merchant_currency()` behavior is covered by focused synthetic tests for the documented accepted shapes already represented by the function: uppercase three-letter string and `{code: ...}` object.
  - Missing, null, malformed, lowercase, non-three-letter, non-string and malformed-object currency inputs return missing/unsupported (`None`) rather than zero, a guessed currency, or an exception.
  - The audit confirms this helper is extraction/normalization only and does not claim that a synthetic test certifies the OpenRetailSchema connector or OAuth.
  - No canonical record is emitted unless it can satisfy the existing canonical currency contract; if the current schema requires more than this helper can prove, keep the output as the normalized currency code and document/test that boundary rather than fabricating fields.
  - Tests are offline, deterministic and synthetic; the existing regression suite remains green.
  - The Builder does not mark the roadmap normalization criterion complete; review decides whether this first slice plus audit evidence is sufficient or whether another normalization slice is required.
- Evidence required:
  - Exact focused test command and passing output for the Loyverse currency normalization tests.
  - Exact full regression command and passing output, locally when available or on the exact produced commit via the existing lightweight CI when useful.
  - Diff limited to `connectors/loyverse.py`, focused tests, and only minimal documentation needed to state a demonstrated boundary.
  - No network access in tests; no token, real payload, customer data, private code, co-author trailer, prohibited attribution, or unsupported vendor/OAuth claim.
- Evidence produced:
  - PR #11 changes one file only: `tests/test_loyverse.py` (+37/-4); no transport or canonical schema code changed.
  - Synthetic tests accept only the two explicit supported merchant currency shapes (`"EUR"` and `{code: "THB"}`) and fail closed to `None` for missing, null, lowercase, wrong-length, non-string and malformed-object inputs.
  - A boundary test demonstrates that `merchant_currency()` returns only a normalized string code and does not emit a canonical record.
  - GitHub Actions run `37119230866` executed on exact produced HEAD `61ebc90497532e8e8dbc66d26049adc3f016a825` and completed successfully. Its Ubuntu job ran `python -m unittest discover -s tests -v` successfully.
  - No focused local command was claimed: no local checkout execution evidence was available in this Builder environment. Full-suite CI on the exact produced commit is the reproducible execution proof for this lot.
- Review verdict: `ACCEPTED` — the bounded currency-normalization slice satisfies every recorded criterion. The helper remains extraction-only, fails closed on unsupported currency shapes, emits no canonical record, and the exact Produced HEAD has a successful full regression run. This acceptance does not certify the connector, OAuth, or live behavior.
- Rework or deferred dependency: `-`
- Next action: Planner should immediately open another independent small lot for the still-incomplete P2 criterion `Audit and normalize connectors/loyverse.py against the canonical contracts`. Do not mark that roadmap criterion complete from this currency-only slice. P1 repeated-import/idempotency remains deferred until a real persistence boundary exists and does not block P2 work.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
