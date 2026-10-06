# Connector execution contract

[Roadmap](ROADMAP.md) · [POS integration registry](POS_INTEGRATIONS.md)

This document defines vendor-neutral execution semantics for read-only connectors. Vendor adapters may expose additional provider details, but consumers can rely on these common rules.

## Pagination

Pagination cursors are **ephemeral transport state**. A cursor may be used only to continue the current provider traversal. `has_more=true` requires a non-empty cursor. A pagination cursor is never a durable synchronization checkpoint and must not be stored or advertised as source progress.

## Checkpoints

A checkpoint is **caller-owned durable source progress**. It must be explicit and non-empty. Its vendor-specific value and advancement rules belong to the adapter contract; consumers must not derive one from a pagination cursor. A connector must advance durable progress only after the records represented by that progress have been successfully traversed and processed.

OpenRetailSchema does not add persistent storage merely to hold checkpoints. Persistence remains a consumer concern until a concrete repository storage contract exists.

## Rate limits and retries

`429` is classified as `rate_limit` and is retryable. A provider `Retry-After` delay, when represented by the common contract, must be explicit and non-negative. The common contract does not invent a retry delay when the provider does not supply one.

Provider `5xx` failures are classified as `provider_unavailable` and are retryable. The generic contract deliberately does not prescribe retry counts, backoff schedules or jitter; an adapter may use bounded retry behavior appropriate to its documented provider constraints.

Authentication (`401`), entitlement (`402`), authorization (`403`) and other permanent client failures are not retryable. The contract rejects attempts to mark permanent failure classes retryable.

## Stable error classes

The common failure kinds are:

- `authentication`
- `authorization`
- `entitlement`
- `rate_limit`
- `provider_unavailable`
- `invalid_request`
- `invalid_response`

Unknown HTTP success/redirection statuses are not accepted by the failure classifier. Provider-specific response validation may produce `invalid_response`; adapters should preserve sanitized provider context separately when safe rather than expanding the stable error taxonomy for every vendor message.

## Evidence boundary

These are OpenRetailSchema contract semantics. They do not by themselves certify any provider implementation. Loyverse remains the first reference connector: its existing synthetic pagination, retry and checkpoint behavior supplies evidence for this generic contract without copying private downstream source. Live Loyverse and OAuth evidence remain separate roadmap gates.
