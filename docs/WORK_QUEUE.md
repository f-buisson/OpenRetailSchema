# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-PRODUCT-NORMALIZATION-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: d5dc24d943150d7153c203e5cfdba886b0ec1a28.
- Scope: normalize Square Catalog ITEM/ITEM_VARIATION responses into canonical v0.1 product records without adding a second transport or inventing missing monetary semantics.
- Acceptance: ITEM_VARIATION is the canonical source identity; parent ITEM supplies the product name; optional SKU/UPC/deleted state are copied only when explicitly valid; missing values remain absent; orphan variations and malformed optional values fail closed; Square minor-unit price is not guessed into canonical decimal money.
- Evidence required: targeted Square tests plus complete public PR CI on the exact branch HEAD before acceptance.
- Evidence produced: implementation and negative/edge synthetic tests committed; execution evidence pending.
- Next action: require CI on the exact PR HEAD, repair any regression or schema mismatch found, and merge only after green proof.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
