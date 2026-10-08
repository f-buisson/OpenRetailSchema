# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P2-LOYVERSE-CHECKPOINT-RECOVERY-01
- Roadmap phase: P2 — Loyverse reference connector
- State: REVIEW
- Base product HEAD: 02ac73ff08ccbf421fdf93432c1d23e95065af97.
- Previous handoff: P4-SQUARE-MONEY-01 accepted through merged PR #40 at 02ac73ff08ccbf421fdf93432c1d23e95065af97; Square Sandbox or seller-account evidence remains deferred.
- Scope: prove that an interrupted paginated Loyverse incremental read can be retried by the caller using the unchanged durable source checkpoint, without retaining the failed traversal's ephemeral cursor.
- Acceptance: a synthetic second-page transport failure returns no checkpoint; a subsequent call on the same client starts from the original `updated_at_min` without `cursor`, re-reads the first page, completes the second page and advances only to the newest processed source timestamp. Internal GET retries are disabled for this scenario.
- Evidence: `tests/test_loyverse_checkpoint.py` covers both attempts, request parameters and final records/checkpoint; targeted and complete regression results are required in the PR checks before acceptance.
- Next action: review the public PR and its test evidence. Authorized live Loyverse connector execution and independent OAuth validation remain deferred P2 gates, not synthetic-test results.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
