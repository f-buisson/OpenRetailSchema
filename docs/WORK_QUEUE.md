# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-ADAPTER-SELECTION-GATE-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: cdc9755b30df3672e66dc0fa10a451dde6bae625.
- Scope: turn the later-adapter policy into a reproducible decision gate and compare all reviewed providers without starting new connector code.
- Acceptance: provider selection requires exact official surface, authorized access path, bounded execution semantics, canonical-semantic confidence, synthetic reproducibility and manageable maintenance cost; current candidates are compared with named missing proof; no provider is promoted solely because documentation exists.
- Evidence required: decision-record review plus normal public PR checks on the exact branch HEAD.
- Evidence produced: the selection record keeps Square as the active certification path, selects no additional adapter, and names Clover only as the first future re-evaluation candidate after authorized sandbox evidence and fabricated mappings.
- Next action: require normal PR checks, merge only if green, then the remaining P4 work is external Square certification and the explicitly deferred StoreLine interface proof; do not start another adapter without new evidence.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
