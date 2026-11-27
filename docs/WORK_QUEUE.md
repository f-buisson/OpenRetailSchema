# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-QUANTITY-BOUNDS-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters; P0 fail-closed correctness.
- State: REVIEW (DRAFT PR, not accepted).
- Base product HEAD: a406eba424fe0a8c5033b2866726b7191ecf817d.
- Previous handoffs: #46–#49, #51 and #52 merged; issue #50 fixed. Do not reopen or duplicate them.
- Scope: enforce Square's documented maximum 12-character decimal quantity for OrderLineItem and OrderReturnLineItem, before Decimal normalization in the existing sale/refund mappers.
- Defect: `Decimal("1e100000")` is finite and positive, and `format(..., "f")` expands an 8-character provider string into 100001 characters. The old function also accepts overlength values, underscores and whitespace. An isolated execution of the exact old function body reproduced these behaviors; this is not a full-module checkout test.
- Evidence: official Square OrderLineItem and OrderReturnLineItem API references (version 2026-09-16) both state quantity maximum length 12 and decimal format. The isolated negative witness accepts `1e100000` and `1e-100000`; the new regression exercises both sale and refund normalization, with valid decimal controls including `.50`.
- Proposed fix: bounded ASCII decimal syntax and length check before Decimal conversion; preserve valid positive decimal quantities and sanitized existing error codes. No transport, schema, persistence or other adapter change.
- Remaining gate: verify exact PR HEAD and author/provenance, run targeted tests and full suite from a clean checkout, inspect the public CI if automatically triggered, and review compatibility before merge. Square Sandbox/seller-account execution, live Loyverse and OAuth OpenRetail remain NOT_RUN.
- Next action: independent review/certification of the single DRAFT PR; do not merge automatically or open another implementation lot.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
