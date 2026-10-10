# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-STORES-COMPLETENESS-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: ACCEPTED
- Base product HEAD: 159e3ed088ae3d58a968b1c0f34d6250bcabac54.
- Previous handoff: P4-SQUARE-LOCATION-COMPLETENESS-01 accepted through merged PR #45; PR and main workflow checks passed on 2026-10-09.
- Scope: extend the per-page `square_locations_missing` guard to `stores.read`. Both operations read `GET /v2/locations`, but only the `sales.read` traversal declared its result key mandatory, so a Locations payload with no `locations` property reported zero stores instead of failing closed.
- Acceptance: a Locations page with no `locations` property fails closed on the first page and on every later page; an explicitly empty list keeps its empty result; `locations: null` keeps `square_result_must_be_array`; cursor cycles, malformed cursors, page budgets and bounded retries are unchanged; `stores.read` still returns provider dictionaries untouched, and `sales.read` entry validation is unaffected.
- Evidence required: targeted Square tests, full regression, JSON example validation, diff check and public PR checks on the exact commit.
- Evidence observed on this branch: `tests.test_square` 30 tests OK; complete regression 137 tests OK, exit 0, zero skips; the 13 JSON examples behave as their names declare; `git diff --check origin/main...HEAD` clean; no secret or client-data pattern in the diff or the commit metadata.
- Mutation evidence: removing the guard from `stores.read`, and narrowing it to the first page only, each turn witnesses red. The second also reddens the `sales.read` witness, which is the point: the two operations now share one rule.
- Next action: none for this lot, accepted through merged PR #46 (merge commit c41fd85f1c18a4ac67a6655af580fdf48b607cb0). Public checks green on the reviewed commit and again on main after merge. The deferred gates are unchanged and unclaimed: an authorized Square Sandbox or seller-account connector run, live Loyverse connector execution, and independent OAuth validation.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
