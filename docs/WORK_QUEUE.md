# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P5-FR-CORE-GUIDES-01
- Roadmap phase: P5 — Adoption and stable evolution
- State: REVIEW
- Base product HEAD: 935759d7a6e601ffc91b0dc25c67272190379457.
- Scope: align the useful French documentation with current repository behavior while keeping English canonical; translate connector execution and adapter selection, and repair stale POS/contribution guidance.
- Acceptance: French POS guidance uses the four evidence levels; Square's synthetic status is current; contribution guidance reflects provenance rules and public CI; connector execution and adapter selection have faithful French guides; English remains the authority for specifications, architecture and roadmap.
- Evidence required: translation diff review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: two new core French guides and aligned French overview/POS/contribution pages; no schema, connector or runtime behavior changes.
- Next action: require normal PR checks, merge only if green, then move to P5 contribution provenance/Apache-2.0 review.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
