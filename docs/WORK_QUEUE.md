# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-POS-DOC-ODOO-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: d52b1d5bcc80bdcabdf38fec224bdbd90fa4c7de.
- Scope: continue the official-provider review with Odoo 19 without starting another adapter; capture only public JSON-2 access, authentication, model-discovery, security and pagination facts that future connector work can safely depend on.
- Acceptance: JSON-2 is the current target; Custom-plan eligibility and bearer-key rotation are explicit; database-specific `/doc` discovery prevents a false universal POS schema; access rights/record rules remain authoritative; offset/limit pagination is documented without inventing a provider cursor or undocumented ceiling; no live/provider evidence or connector support is claimed.
- Evidence required: documentation diff review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: official Odoo 19 JSON-2, ORM search/read, legacy RPC migration and Point of Sale product documentation reviewed on 2026-10-07; no database, API key, provider payload or connector execution used.
- Next action: require normal PR checks, merge only if green, then continue the P4 evidence cycle with Epos Now rather than implementing Odoo until authorized Custom-plan access and synthetic canonical mappings justify it.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
