# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-POS-DOC-EPOSNOW-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: 0b06521d167cf78b12b12400dcc7cedce29c5dde.
- Scope: complete the named official-provider review cycle with Epos Now without starting another adapter; capture only public versioning, authentication, API-device access, pagination, quota and transaction-time boundaries that future connector work can safely depend on.
- Acceptance: V4 is preferred where current equivalents exist; per-device Basic credentials and rotation are explicit; account-specific API limits are not replaced by an invented global quota; 200-record page-number pagination is explicit; transaction timezone/offset uncertainty blocks canonical event-time emission; no live/provider evidence or connector support is claimed.
- Evidence required: documentation diff review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: official Epos Now authentication, API-device setup/limits, pagination, V4 reference, product/transaction references and transaction-model introduction reviewed on 2026-10-07; no account, API device, token, provider payload or connector execution used.
- Next action: require normal PR checks, merge only if green, then reassess the remaining P4 criteria instead of starting an Epos Now adapter until authorized access, timezone evidence and synthetic mappings justify it.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
