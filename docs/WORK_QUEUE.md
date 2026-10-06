# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-POS-DOC-LIGHTSPEED-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: 0424d42bde6f0ca92882dc63dfdea7fb4343bd76.
- Scope: continue the official-provider review with Lightspeed Retail X-Series without starting another adapter; capture only public access, scope, pagination, quota and plan-boundary facts that future connector work can safely depend on.
- Acceptance: current API-version direction is explicit; OAuth and personal-token boundaries are distinct; minimum read scopes are recorded; pagination and rate-limit semantics are traceable to official sources; no live/provider evidence or connector support is claimed.
- Evidence required: documentation diff review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: official Lightspeed X-Series introduction, authorization, scopes, pagination, rate-limit, product and sales references reviewed on 2026-10-06; no account, token, provider payload or connector execution used.
- Next action: require normal PR checks, merge only if green, then continue the same P4 evidence cycle with Clover rather than implementing Lightspeed until authorized access and synthetic canonical mappings justify it.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
