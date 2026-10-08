# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P2-LOYVERSE-EXPLICIT-PRICE-01
- Roadmap phase: P2 — Loyverse reference connector
- State: REVIEW
- Base product HEAD: 83b8c6ab86790b2124709c4a38f8b2fc15836491.
- Previous handoff: P2-LOYVERSE-PRODUCT-PRICE-01 accepted through merged PR #42, with 119 complete regression tests and public checks green.
- Scope: reject explicitly supplied malformed Loyverse product prices at the canonical product boundary; preserve missing/null versus zero and do not alter the shared signed money formatter.
- Acceptance: unsupported types (including floats, booleans, strings, collections), non-finite Decimals and negative numeric prices raise sanitized `invalid_product_price`; missing/null stay absent, numeric zero and positive amounts remain intact; unknown merchant currency does not invent a price; receipt/refund money remains unchanged.
- Evidence required: targeted product/money tests, complete repository regression, JSON fixture validation and public PR checks on the exact commit.
- Evidence observed on this branch: targeted Loyverse suites 23, 7 and 3 tests OK; complete regression 120 tests OK; the 13 JSON examples behave as their names declare; `git diff --check` clean. Three mutations killed: removing the guard, widening it to refuse a genuinely absent price, and dropping its null check each turn witnesses red.
- Next action: review this lot and its public CI evidence before acceptance. Authorized live Loyverse connector execution and independent OAuth validation remain deferred P2 gates, still unclaimed.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
