# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-POS-DOC-CLOVER-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: aee4ce5af7d2d49aba9d17d953e9f0c78fd99a65.
- Scope: continue the official-provider review with Clover without starting another adapter; capture only public auth, permissions, pagination/completeness, rate-limit, timestamp and history-boundary facts that future connector work can safely depend on.
- Acceptance: sandbox and production auth are distinct; least-privilege data permissions are explicit; top-level pagination and nested expansion limits are recorded; request/concurrency limits and 429 behavior are traceable; millisecond timestamps and order-query history boundaries cannot be mistaken for absence.
- Evidence required: documentation diff review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: official Clover REST usage, OAuth, permissions, sandbox token, pagination, rate-limit, timestamp and order references reviewed on 2026-10-06; no account, token, merchant payload or connector execution used.
- Next action: require normal PR checks, merge only if green, then continue the P4 evidence cycle with Odoo rather than implementing Clover until authorized sandbox access and synthetic canonical mappings justify it.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
