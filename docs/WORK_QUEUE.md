# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-REFUND-NORMALIZATION-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: f63b00dc0db3ba5cedf503f77095bfba389df94b.
- Scope: normalize only unambiguous completed Square refunds by combining PaymentRefund event time with OrderReturn itemization. Do not invent money conversion or allocation across multiple completed refunds.
- Acceptance: PaymentRefund.created_at is the canonical occurrence time; PaymentRefund.order_id links to the refund order; each returned line requires source order/line identity, CatalogItemVariation ID and positive quantity; multiple completed refunds for one return order fail closed; money remains absent.
- Evidence required: targeted Square refund tests, complete local regression suite, and public PR CI on the exact branch HEAD.
- Evidence produced: official Square Refunds/Orders documentation re-checked on 2026-10-06; targeted Square tests passed 16/16 and complete local suite passed 111/111 on the branch after the schema-safe source-link fix.
- Next action: open/review the PR, require CI on the exact PR HEAD, repair any regression, and merge only after green proof.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
