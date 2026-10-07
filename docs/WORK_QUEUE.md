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
- Integrated by: PR #39, merge commit `281a17daf012fa4bef1389d6042cf178b46591ef`.
- Scope: publish a migration/versioning policy grounded in the released v0.1 schema and implemented connector manifest, plus lock fail-closed handling of an unknown canonical schema version.
- Acceptance: repository/schema/manifest/provider versions remain independent; pre-1.0 breaking changes create new versioned contracts; historical schema meaning is stable; migration notes distinguish lossless, lossy and unsupported conversion; closed-schema additions are not falsely called compatible; adding a mandatory common connector operation is a manifest break; 1.0 mechanics are documented without declaring readiness.
- Evidence: PR #39 merged after the exact branch HEAD `d909996b953d5ddfcc4ce0eaecb3cd789216f971` completed the public Tests workflow successfully. The merged policy and synthetic `0.2.0` fixture lock fail-closed handling of an unknown canonical schema version.
- Remaining P5 gates: SDK and service API stay intentionally unstarted until real consumers justify them; the 1.0 gate stays intentionally unstarted until v0.1 adoption and at least one live-tested reference connector provide evidence.
- Next action: prefer authorized live evidence for Loyverse or Square when access exists. Without it, reassess only independent correctness/security/provenance defects or demonstrated downstream duplication; do not invent speculative infrastructure or another adapter.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
