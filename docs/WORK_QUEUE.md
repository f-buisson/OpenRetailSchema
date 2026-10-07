# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-CONTRIBUTION-CONTRACT-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: 2f9c12d3fc793c666ed98d2daba595047d93ccec.
- Scope: make external POS contributions reproducible and license-safe without adding connector code; align the contribution guide, issue form, pull-request template and CI documentation with repository reality.
- Acceptance: provider/version and official sources are explicit; synthetic fixture or fabricated mapping intent is required; provenance and redistribution rights are recorded; missing/unknown semantics are not guessed; local test reporting and public CI roles are distinct; no secrets or real provider payloads are requested.
- Evidence required: review of issue #1 and contribution surfaces plus normal public PR checks on the exact branch HEAD.
- Evidence produced: issue #1 is open as the community entry point; the strengthened proposal form and new pull-request template make evidence, provenance, test reporting and safety expectations explicit; stale statements claiming no hosted CI are removed.
- Next action: require normal PR checks, merge only if green, then evaluate the remaining P4 adapter-selection gate without starting another adapter prematurely.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
