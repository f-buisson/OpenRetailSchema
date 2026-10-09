# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-LOCATION-COMPLETENESS-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: ACCEPTED
- Base product HEAD: 7cb938f2a2bf4b7483a83e4c3757c4bd74d8e39a.
- Previous handoff: P4-SQUARE-PAGINATION-CYCLE-01 accepted through merged PR #44, with 125 complete regression tests and public checks green.
- Scope: refuse an incomplete Square location set instead of reporting it as an empty one. A Locations page with no `locations` property at all is now distinguished from an explicitly empty list, on the first page and on every later page, and every entry is validated before any Orders search is sent.
- Acceptance: malformed locations fail closed with sanitized errors; duplicates across pages fail closed; explicitly empty locations retain the existing empty result; eleven valid locations retain ten-ID batching; no Orders request occurs after invalid location discovery.
- Evidence required: targeted Square tests, full regression, JSON example validation, diff check and public PR checks on the exact commit.
- Evidence observed on this branch: `tests.test_square` 27 tests OK; complete regression 134 tests OK, exit 0, zero skips; the 13 JSON examples behave as their names declare; `git diff --check` clean.
- Defect found and fixed in review: the published commit validated location entries but left a missing `locations` property indistinguishable from an empty list, because `_paginate_get` defaults an absent result key to `[]`. Measured on that commit, an absent property on the first page returned no sales at all, and an absent property on a later page carried on with a PARTIAL location set and searched orders anyway, reporting incompleteness as success. The requirement is declared per call, so no other operation changed in this lot.
- Mutation evidence: removing the guard, checking only the first page, and widening the guard to every GET read each turn witnesses red. The third mutation initially SURVIVED, which showed nothing pinned the scope; a witness was added so a locations error code can never answer a catalog or inventory payload.
- Next action: none for this lot, accepted through merged PR #45 (merge commit ff5ac219325751422c929dccb816287f255bc486). Public checks green on the reviewed commit and again on main after merge. The three deferred gates stay open: authorized Square Sandbox or seller-account execution, live Loyverse connector execution and independent OAuth validation.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
