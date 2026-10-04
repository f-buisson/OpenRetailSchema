# Work handoff

This file coordinates small reviewable lots between planning, implementation and review.

The repository state is authoritative. Always refresh `main`, `docs/ROADMAP.md` and this file before changing anything.

## State machine

Allowed states:

- `IDLE` — no lot is currently assigned.
- `READY` — a scoped lot has acceptance criteria and may be implemented.
- `BUILDING` — implementation has started from the recorded base.
- `REVIEW` — implementation is complete enough to review.
- `ACCEPTED` — evidence satisfies the recorded acceptance criteria.
- `REWORK` — review found specific defects that must be corrected.
- `DEFERRED` — this specific lot cannot currently be completed because it depends on an external condition, authorization, live account, hardware, unavailable evidence or other dependency. DEFERRED never blocks the project.

Allowed transitions:

```
IDLE -> READY
READY -> BUILDING
BUILDING -> REVIEW
REVIEW -> ACCEPTED
REVIEW -> REWORK
REWORK -> BUILDING
REVIEW -> DEFERRED
DEFERRED -> READY
ACCEPTED -> READY
```

Do not skip `REVIEW` to mark implementation accepted.

## Non-blocking rule

The project must keep advancing while useful independent work exists.

1. A dependency may defer one lot, but it must never freeze the global queue.
2. When a lot becomes `DEFERRED`, record the exact dependency and the condition that would make that lot actionable again.
3. In the same reviewer/planner cycle when practical, move on to the next independent incomplete roadmap criterion and create a new `READY` lot.
4. If the first incomplete criterion of the highest-priority phase depends on unavailable external evidence, preserve that criterion as incomplete and work on the next independent criterion without falsely marking the deferred criterion complete.
5. Human access, vendor authorization, live credentials, external hardware or unavailable real data are reasons to defer that specific proof, not reasons to stop development, tests, documentation, adapters, fixtures or other independent roadmap work.

## Concurrency rules

1. Record the observed product HEAD before starting a transition.
2. Immediately before writing, refresh HEAD and this file.
3. A commit that only updates `docs/WORK_QUEUE.md` for coordination is an expected handoff change, not a product-base collision.
4. If product files changed unexpectedly, re-evaluate the lot instead of overwriting newer work.
5. Only the phase responsible for the current transition may change the state.
6. A lot is not complete because code exists; completion requires reproducible evidence.
7. Cosmetic edits do not justify a state transition.
8. If a run ends after code changes but before evidence is complete, leave the state at `BUILDING` or `REVIEW` as appropriate and describe the missing evidence.
9. Never leave the global workflow waiting on one unavailable dependency when another useful independent roadmap item can be worked.

## Current handoff

- Work ID: `P2-LOYVERSE-NORM-AUDIT-01`
- Roadmap phase: P2 — audit and normalize `connectors/loyverse.py` against canonical contracts
- State: `READY`
- Base product HEAD: `181bc1a532507d5ff2a4f2758ec841300a95d751`.
- Classification: consolidation of behavior already present in OpenRetailSchema. Product and sale normalization are implemented and accepted; pagination is already independently complete. `docs/LOYVERSE_REUSE.md` was reviewed before opening this lot. External Alertarif/PlanCaisse evidence is design/test input only and must not be copied or relabeled as repository certification.
- Scope: perform a bounded canonical-coverage audit of the current Loyverse adapter and close only concrete gaps required for the existing P2 normalization criterion. Prefer reusing `source_decimal`, `source_external_id`, `canonical_money`, `canonical_product`, `canonical_sale`, `_opaque_string` and `_event_timestamp`; do not introduce parallel helpers or a second mapping path. Determine explicitly whether the canonical `activity` entity has a documented, semantically safe Loyverse source in the currently supported public resources. If not, keep activity unsupported rather than guessing from shifts/receipts and record that boundary in the connector capability/evidence documentation.
- Acceptance criteria: (1) every canonical entity the connector actually emits is validated by a reproducible targeted test against the v0.1 schema; (2) at least one negative/limit test per emitted entity proves malformed required source data fails closed; (3) monetary optionality tests preserve missing/null != explicit zero and reject unsupported numeric coercion; (4) no undocumented source field is mapped by inference and no `activity` record is fabricated from semantically insufficient source data; (5) any public capability/provenance/unsupported boundary discovered by the audit is reflected in the relevant English canonical documentation without claiming live certification; (6) the full local regression suite passes on the Produced HEAD; (7) if these checks demonstrate that canonical normalization is complete for the supported mapping surface, the Builder may propose the roadmap checkbox change in the same product lot, but must not mark unrelated P2 criteria complete.
- Required evidence: exact targeted test command/results for product and sale canonical validation plus any new boundary test; exact full regression command/result; diff showing any documentation/roadmap update is supported by code/tests. Use synthetic fixtures only. CI is not required unless local execution cannot provide reproducible proof or a platform-specific check materially adds evidence.
- Exclusions: no retries, checkpoints, OAuth, live account calls, persistence, new pagination, SDK/API layer, real payloads, tokens, customer/employee data, private source code or speculative shift-to-activity semantics.
- Debt check: 0 open PRs at planning time; no TODO/FIXME result found in repository search; no duplicate canonical mapper found. This consolidation lot reduces ambiguity around the broad normalization checkbox and does not add a competing implementation.
- Next action: Builder transitions `READY -> BUILDING`, audits the existing mapping surface from this exact base, adds only the smallest missing code/tests/docs needed by the criteria above, then records Produced HEAD and reproducible evidence before handing the same Work ID to REVIEW.

## Handoff discipline

Keep this file compact. Replace the current handoff when a new lot starts; durable product decisions belong in the relevant specification or documentation, not in this coordination file. A deferred lot remains documented in durable roadmap/evidence notes, but the active handoff must move to independent useful work instead of stopping the project.
