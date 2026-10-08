# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P2-LOYVERSE-PRODUCT-PRICE-01
- Roadmap phase: P2 — Loyverse reference connector
- State: ACCEPTED
- Base product HEAD: c3343b6d26c4a0b0dcc1aeecb126836e286d24c2.
- Previous handoff: P2-LOYVERSE-CHECKPOINT-RECOVERY-01 accepted through merged PR #41; PR and main workflow checks passed on 2026-10-08.
- Scope: reject explicitly negative Loyverse product prices at the product-mapping boundary without changing the signed money formatter shared with refund contexts.
- Acceptance: negative integer and decimal variant prices raise a sanitized `invalid_product_price`; zero, missing and positive prices retain existing semantics; generic signed money formatting remains unchanged.
- Evidence required: targeted product/money tests, complete repository regression and public PR checks on the exact commit.
- Evidence observed on 88fed3d9aef66661d0647a258bdbe62fb5557a17: targeted Loyverse suites 22, 7 and 3 tests OK; complete regression 119 tests OK; the 13 JSON fixtures behave as their names declare; public checks green on the reviewed commit and again on main after merge.
- Next action: none for this lot, accepted through merged PR #42 (merge commit a2b6c105ec6c24a9497fd92616603ee6db4c61b1). Authorized live Loyverse connector execution and independent OAuth validation remain deferred P2 gates, still unclaimed.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
