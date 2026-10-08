# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P2-LOYVERSE-PRODUCT-PRICE-01
- Roadmap phase: P2 — Loyverse reference connector
- State: REVIEW
- Base product HEAD: c3343b6d26c4a0b0dcc1aeecb126836e286d24c2.
- Previous handoff: P2-LOYVERSE-CHECKPOINT-RECOVERY-01 accepted through merged PR #41; PR and main workflow checks passed on 2026-10-08.
- Scope: reject explicitly negative Loyverse product prices at the product-mapping boundary without changing the signed money formatter shared with refund contexts.
- Acceptance: negative integer and decimal variant prices raise a sanitized `invalid_product_price`; zero, missing and positive prices retain existing semantics; generic signed money formatting remains unchanged.
- Evidence required: targeted product/money tests, complete repository regression and public PR checks on the exact commit.
- Next action: review this lot and its CI evidence before acceptance. Authorized live Loyverse connector execution and independent OAuth validation remain deferred P2 gates.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
