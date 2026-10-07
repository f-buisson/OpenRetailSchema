# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-MONEY-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: 0bbb0618858a697ac0b82b5f284986dd72e6d61b.
- Scope: convert Square `CatalogItemVariation.price_money` into canonical `sale_price` through a single minor-unit implementation, and only where Square's pricing semantics are unambiguous.
- Acceptance: `FIXED_PRICING` with a valid Money yields a canonical price; an explicit zero stays zero; a missing price stays absent and is never rewritten as zero; `VARIABLE_PRICING` carrying a price fails closed; unsupported currency, non-integer amount, boolean amount and negative price all fail closed; documented exponents are `AUD`/`CAD`/`EUR`/`GBP`/`USD` 2 and `JPY` 0; sales and refunds normalization is unchanged; no shared money abstraction is introduced for a single caller.
- Evidence required: targeted Square tests including negative and boundary Money cases, the complete repository suite, canonical schema validation of emitted records, and the public PR checks on the exact branch HEAD.
- Evidence produced: minor-unit conversion with documented exponents; negative product price rejected after measurement showed the canonical money pattern would accept the sign; boolean amount rejected because Python booleans are integers; emitted records validated against `schemas/v0.1/record.schema.json`; provider documentation and roadmap corrected where their stated reason for absent money no longer held.
- Next action: await the public PR result. Sales and refunds money mapping stays out of scope until its allocation and tax semantics are established; the authorized Square Sandbox or seller-account run remains the outstanding P4 evidence.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
