# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-RFC3339-TIMESTAMPS-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: REVIEW
- Base product HEAD: a54e382c0474ad0de55e21955481c63acbcdac6c.
- Previous handoff: P4-SQUARE-STORES-COMPLETENESS-01 accepted via merged PR #46; no reopening.
- Scope: require RFC 3339 extended date-time syntax before mapping Square completed-order `closed_at` and completed PaymentRefund `created_at` into canonical `occurred_at`.
- Defect: Python `datetime.fromisoformat` accepts space separators, basic/week dates and offsets with seconds or without colons; these are outside the published canonical RFC 3339 contract. The old function accepted seven such invalid forms in a local reproduction using its exact implementation.
- Acceptance: reject malformed/non-RFC-3339 timestamps with the existing sanitized Square error codes, preserve valid `Z` and numeric offsets, fractional seconds and case-insensitive `t`/`z`; cover both sale and refund mapping without changing raw transport.
- Evidence: PR #49 is OPEN/DRAFT. On its prior HEAD `94ae059b`, Python 3.12.14 with jsonschema 4.26.0 passed 147/147 synthetic tests on 2026-10-23. Independent isolated review subsequently proved that invalid offset minutes such as `+00:60` were still accepted by `datetime.fromisoformat` and returned unchanged; the existing PR now constrains offset hours to 00–23 and minutes to 00–59, with sale/refund regressions.
- Remaining gate: rerun targeted Square tests, the full regression, canonical examples and diff checks from a clean checkout on the *new exact branch HEAD*. The 147/147 evidence predates this offset fix and must not be represented as certification of the new commit. Square Sandbox/seller-account execution, live Loyverse and OAuth OpenRetail remain NOT_RUN.
- Next action: finish PR #49 review and exact-HEAD certification before acceptance; do not open a duplicate PR or merge automatically.


## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
