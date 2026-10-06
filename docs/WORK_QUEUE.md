# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-PAGINATION-SAFETY-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: a46432bb491dcc851dea80773b5e3ef6c06dff8b.
- Scope: lock the existing Square GET/POST pagination page budget into regression tests so a repeated provider cursor cannot cause unbounded transport calls. Do not change provider semantics or claim live evidence.
- Acceptance: repeated GET and POST cursors stop at the configured `max_pages`; `max_pages=1` performs exactly one transport call; cursor propagation remains explicit.
- Evidence required: targeted pagination-safety tests plus the complete public PR CI on the exact branch HEAD.
- Evidence produced: implementation inspection confirms both Square pagination paths are bounded by `max_pages`; dedicated synthetic regression tests cover GET, POST and the one-page edge case. No local test execution is claimed for this lot.
- Next action: require public PR CI on the exact branch HEAD, repair any regression, and merge only after green proof.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
