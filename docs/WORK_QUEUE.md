# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P5-PROVENANCE-01
- Roadmap phase: P5 — Adoption and stable evolution
- State: REVIEW
- Base product HEAD: 3e4fac1857f07524418b570e85fab36ac3a56449.
- Scope: establish a reproducible repository provenance/licensing baseline and a review gate for any future incorporated third-party material.
- Acceptance: complete commit and PR history are checked for accepted contributors; vendored/generated third-party source is searched; direct Python and CI dependencies have upstream licences recorded; external references remain references rather than copied source; future third-party code/fixtures require source, exact version, licence compatibility and preserved notices before merge.
- Evidence required: repository history/tree/code-search review plus upstream licence checks and normal public PR checks on the exact branch HEAD.
- Evidence produced: 237/237 commits and 36/36 historical PRs are attributable to `f-buisson`; the 88-entry tree contains no vendored/third-party/generated source area; `jsonschema`, `actions/checkout` and `actions/setup-python` use permissive MIT terms upstream; named external SDK/connectors appear only in the research-reference document.
- Next action: require normal PR checks, merge only if green, then move to the P5 migration/versioning-policy criterion.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
