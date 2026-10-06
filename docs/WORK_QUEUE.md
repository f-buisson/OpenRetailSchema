# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-POS-DOC-REVIEW-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: 3f40f7b624e68af90cc884193d383a8096c2cfb7.
- Scope: refresh the stale integration registry after the merged Square work and perform the next independent official-documentation review for Shopify without starting another adapter.
- Acceptance: Square registry status matches repository reality; Shopify claims are traceable to current official sources; pagination, throttling, order-history entitlement and POS-origin uncertainty are explicit; no live or connector evidence is claimed.
- Evidence required: documentation diff review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: official Shopify GraphQL Admin documentation reviewed on 2026-10-06; no account, token, provider payload or connector execution used.
- Next action: require normal PR checks, merge only if green, then continue the P4 vendor evidence review with the next system rather than implementing Shopify until POS-origin semantics and authorized access justify it.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
