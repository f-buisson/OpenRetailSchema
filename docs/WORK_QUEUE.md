# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P5-VERSIONING-01
- Roadmap phase: P5 — Adoption and stable evolution
- State: ACCEPTED
- Base product HEAD: 639400e8a829dee0a06bc2efc18384eaa2877dba.
- Accepted product HEAD: 281a17daf012fa4bef1389d6042cf178b46591ef.
- Scope: publish a migration/versioning policy grounded in the released v0.1 schema and implemented connector manifest, plus lock fail-closed handling of an unknown canonical schema version.
- Acceptance: repository/schema/manifest/provider versions remain independent; pre-1.0 breaking changes create new versioned contracts; historical schema meaning is stable; migration notes distinguish lossless, lossy and unsupported conversion; closed-schema additions are not falsely called compatible; adding a mandatory common connector operation is a manifest break; 1.0 mechanics are documented without declaring readiness.
- Evidence required: targeted unknown-schema-version regression plus complete public PR checks on the exact branch HEAD.
- Evidence produced: versioning/migration policy, compatibility/architecture alignment and a synthetic `0.2.0` product fixture that the current `0.1.0` validator must reject.
- Acceptance evidence: PR #39 merged to `main` at `281a17daf012fa4bef1389d6042cf178b46591ef`; the roadmap records the versioning policy and unknown-schema-version regression as complete.
- Next action: do not start speculative SDK/service work. Prefer authorized live connector evidence when access is available; otherwise select a small independent correctness, security, provenance or downstream-reuse task.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
