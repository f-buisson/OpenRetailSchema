# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P4-SQUARE-OFFICIAL-BOUNDARIES-01
- Roadmap phase: P4 — Square next, then evidence-backed adapters
- State: READY
- Base product HEAD: dfe5cfa24256dc6dd15ec03b1bd526e18ed7c71e.
- Scope: complete the current official-evidence review for Square scopes, pagination, access requirements, webhook relevance, rate-limit guidance and any documented plan restrictions. Do not add persistence, write operations or speculative abstractions.
- Acceptance: every statement added to `docs/SQUARE.md` is backed by current public Square documentation; unsupported or irrelevant surfaces are explicit; the roadmap criterion is checked only if its full wording is evidenced.
- Evidence required: current official links and a documentation-only review against the merged Square read surface.
- Evidence produced: none yet for this lot. PR #24 is accepted separately: exact head `ad79607bd04f3573cb5ab4aa368ac88d6e5df5a3` passed workflow run `37484603967` and merged as `dfe5cfa24256dc6dd15ec03b1bd526e18ed7c71e`.
- Next action: review current official Square documentation and update only evidence/boundaries that can be proven without a live account.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
