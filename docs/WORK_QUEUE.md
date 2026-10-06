# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-SALE-NORMALIZATION-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: b9f6ad6843b2bee9bc4de81c0eef434bb78ec4ca.
- Scope: normalize only Square orders whose semantics are sufficient for canonical v0.1 sales. Do not invent money conversion, refund timestamps or custom-product identity.
- Acceptance: non-completed orders are not emitted; completed orders use `closed_at`; each line requires a Square line UID, CatalogItemVariation ID and positive decimal quantity; Square minor-unit money stays absent; return-bearing orders fail closed instead of being mislabeled as sales.
- Evidence required: targeted Square tests plus complete public PR CI on the exact branch HEAD.
- Evidence produced: implementation and synthetic positive/negative tests committed; official Square Order and OrderReturn semantics re-checked on 2026-10-06. The review established that `OrderReturn` lacks the event timestamp required for canonical refund `occurred_at`, so refund normalization remains a separate incomplete roadmap item.
- Next action: require CI on the exact PR HEAD, repair any regression/schema mismatch, and merge only after green proof.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
