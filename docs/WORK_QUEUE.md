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

- Work ID: `P2-LOYVERSE-NORM-04`
- Roadmap phase: `P2 — Loyverse reference connector`
- State: `REVIEW`
- Observed main HEAD: `57bd1f60838222cbfe946604ece7098122f65d94`
- Produced HEAD: `1f1c4c80050483929bf535c42647d4b865b0cbc2`
- Deferred predecessor: P1 repeated-import/idempotency remains incomplete until a real persistence boundary exists; do not invent storage only to close it.
- Reuse classification: OpenRetailSchema already has accepted Loyverse helpers for merchant currency, finite source decimals and opaque source IDs. External project evidence confirms unknown-versus-zero and merchant-currency behavior as design/test input only; it does not certify this connector.
- Scope: add one bounded raw-to-canonical money normalization helper plus focused synthetic tests. Compose an already-validated finite source numeric field with an already-validated merchant currency code into the canonical v0.1 money shape `{amount, currency}`. Preserve zero as zero and missing/invalid amount as unknown; never invent a currency or amount. Serialize `Decimal` deterministically as a plain JSON-compatible decimal string without exponent notation or binary-float conversion. Do not build full product/sale mappings, tax inference, retries, checkpoints, live calls or OAuth behavior in this lot.
- Acceptance criteria:
  - A focused helper in `connectors/loyverse.py` returns a canonical v0.1 money object only when both the source amount and uppercase three-letter merchant currency are valid under the existing helpers/contracts.
  - Explicit numeric zero yields an amount string representing zero and is never treated as missing.
  - Missing/null/unsupported/non-finite amounts return/fail closed as unknown rather than `{amount: "0", ...}`.
  - Missing or malformed currency returns/fail closed; there is no default currency.
  - Finite integer and `Decimal` values are serialized exactly to non-exponent decimal strings accepted by the canonical money schema, including negative/refund-like values and fractional precision.
  - Focused fabricated tests cover zero, negative, fractional, missing amount, invalid amount, missing currency and malformed currency; existing currency/numeric/source-ID/pagination behavior remains unchanged.
  - The full regression suite passes on the exact produced product commit.
- Evidence required:
  - Exact product commit SHA and diff limited to the bounded helper/tests plus necessary coordination.
  - Exact focused test command and passing output.
  - Exact full regression command and passing output, locally or through one justified lightweight CI run on the exact product commit.
  - Confirmation that tests use fabricated data only and that no secret, token, real payload, customer data, private code, co-author trailer or unsupported live/certification claim was introduced.
- Evidence: Product commit `1f1c4c80050483929bf535c42647d4b865b0cbc2` remains unchanged. Commits after it modify only coordination and `.github/workflows/tests.yml`; no product file changed. GitHub Actions run `37154602436` on `57bd1f60838222cbfe946604ece7098122f65d94` completed successfully. Job `111295306071` ran the exact focused command `python -m unittest tests.test_loyverse.LoyverseTests.test_canonical_money_serializes_finite_values_exactly tests.test_loyverse.LoyverseTests.test_canonical_money_preserves_unknown_amount tests.test_loyverse.LoyverseTests.test_canonical_money_requires_valid_merchant_currency -v` successfully, then ran `python -m unittest discover -s tests -v` successfully. The tests are fabricated and the bounded product diff introduces no live call, OAuth behavior, token, real payload, customer data, private code or certification claim.
- Limits: this lot does not complete roadmap-wide Loyverse normalization, tax semantics, end-to-end mappings, retries/checkpoints or live/OAuth evidence. The P2 roadmap criterion remains incomplete.
- Next action: reviewer certifies the recorded evidence against the unchanged Produced HEAD and issues ACCEPTED, REWORK or DEFERRED without expanding scope.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
