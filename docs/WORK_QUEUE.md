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
- Evidence: isolated Python reproduction of the exact original helper observed 7 accepted invalid examples; the patched helper passed 2 local `unittest` methods with subtests for 8 invalid and 5 valid strings. This is NOT a fresh-checkout test of the full repository.
- Remaining gate: execute `python -m unittest tests.test_square tests.test_square_refunds -v`, then `python -m unittest discover -s tests -v`, canonical validation and diff checks on the PR HEAD; public PR checks may provide independent confirmation. Do not claim live Square or OAuth certification.
- Next action: review the proposed PR and its exact-HEAD tests; only mark ACCEPTED after reproducible suite evidence.

