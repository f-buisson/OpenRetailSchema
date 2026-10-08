# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-PAGINATION-CYCLE-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: BUILDING
- Base product HEAD: 6e2aefae201837c11dc63e100042217b930ef181.
- Previous handoff: P2-LOYVERSE-EXPLICIT-PRICE-01 accepted through merged PR #43, with 120 complete regression tests and public checks green.
- Scope: reject repeated Square pagination cursors on GET and POST reads, including non-adjacent cycles; reject falsy non-string cursors while preserving absent, null and empty-string termination.
- Acceptance: repeated cursors raise sanitized `square_cursor_repeated`; malformed cursors raise `square_cursor_must_be_string`; no extra transport calls after detection; distinct cursors continue; page limits, retries and mappings remain unchanged.
- Evidence required: targeted Square tests including negative cases, full repository regression, JSON example validation, diff check and public PR checks on the exact commit.
- Evidence observed: code and synthetic tests prepared; execution and public checks not yet claimed.
- Next action: execute targeted and complete tests, review, then open a PR and accept only after green checks. Authorized Square Sandbox execution, live Loyverse connector execution and independent OAuth validation remain deferred and unclaimed.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
