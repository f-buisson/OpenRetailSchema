# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states: `IDLE`, `READY`, `BUILDING`, `REVIEW`, `ACCEPTED`, `REWORK`, `DEFERRED`.

Do not skip `REVIEW` to mark implementation accepted. A dependency may defer one lot, but it must never freeze independent work. Record the observed product HEAD before starting a transition; if product files changed unexpectedly, re-evaluate rather than overwrite newer work. Completion requires reproducible evidence, not merely code.

## Current handoff

- Work ID: P3-READ-COMPLETENESS-01
- Roadmap phase: P3 — Connector contract (shared semantics for downstream consumers); P0 fail-closed correctness.
- State: ACCEPTED
- Base product HEAD: c7002239f96677e97118336b56776d7efbd43039.
- Previous handoffs: #46–#49 and #51–#53 merged; issue #50 fixed. P4-SQUARE-QUANTITY-BOUNDS-01 is accepted (PR #53, merge `c700223`). Do not reopen or duplicate them.
- Scope: make read completeness and related-data failure handling explicit in the execution contract. That means `ReadOutcome` (scope, missing, checkpoint), `proves_absence`, `related_data_may_be_missing`, and the English and French documentation. No adapter, transport, schema or persistence change.
- Defect class: on 2026-11-27 a downstream consumer reproduced two failure modes in its own connectors, with end-to-end synthetic tests:
  - A traversal stopped by a repeated page or by a page budget removed records it had not read when it was applied as a full catalogue. Applied as a patch onto the empty baseline left by a restart, it replaced the catalogue.
  - A transient 429 or 5xx on the tax list, reported as "tax rates missing", erased the known rate of every record at the next full read.
- Contract gap: ORS adapters already fail closed on the first mode (repeated cursor, `square_pagination_limit_exceeded`), but the contract did not state it. It said nothing about the second.
- Evidence: `tests/test_read_outcome.py` adds 8 tests. The local full suite passes 167/167 from the PR head. All 9 mutants of the new rules are killed, with the control green before and after.
- Next action: none for this lot. It is accepted through merged PR #54 (merge commit 494760cd5030d2631adbf5454e4df1153cee03c9). The owner approved it at the reviewed head d1f288b, whose public checks were green. The deferred gates are unchanged and unclaimed: the Square Sandbox or seller-account run, live Loyverse and OAuth OpenRetail remain NOT_RUN for OpenRetailSchema adapters.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in specifications or provider documentation. Deferred external live/OAuth proof remains incomplete without blocking independent implementation.
