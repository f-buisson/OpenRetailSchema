# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-LOCATION-COMPLETENESS-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: BUILDING
- Base product HEAD: 7cb938f2a2bf4b7483a83e4c3757c4bd74d8e39a.
- Previous handoff: P4-SQUARE-PAGINATION-CYCLE-01 accepted through merged PR #44, with 125 complete regression tests and public checks green.
- Scope: validate every Square location ID before sales search; refuse malformed and repeated IDs without silently truncating the location set or querying orders twice.
- Acceptance: malformed locations fail closed with sanitized errors; duplicates across pages fail closed; explicitly empty locations retain the existing empty result; eleven valid locations retain ten-ID batching; no Orders request occurs after invalid location discovery.
- Evidence required: targeted Square tests, full regression, JSON example validation, diff check and public PR checks on the exact commit.
- Evidence observed: pending; no repository tests have been executed for this lot yet.
- Next action: run tests, review the exact diff, publish a PR only after local checks pass, and preserve the three deferred live Square/Loyverse/OAuth gates.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
