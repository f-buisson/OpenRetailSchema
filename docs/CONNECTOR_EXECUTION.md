# Connector execution contract

[Roadmap](ROADMAP.md) · [POS integration registry](POS_INTEGRATIONS.md)

This document defines vendor-neutral execution semantics for read-only connectors. Vendor adapters may expose additional provider details, but consumers can rely on these common rules.

## Pagination

Pagination cursors are **ephemeral transport state**. A cursor may be used only to continue the current provider traversal. `has_more=true` requires a non-empty cursor. A pagination cursor is never a durable synchronization checkpoint and must not be stored or advertised as source progress.

## Checkpoints

A checkpoint is **caller-owned durable source progress**. It must be explicit and non-empty. Its vendor-specific value and advancement rules belong to the adapter contract; consumers must not derive one from a pagination cursor. A connector must advance durable progress only after the records represented by that progress have been successfully traversed and processed.

OpenRetailSchema does not add persistent storage merely to hold checkpoints. Persistence remains a consumer concern until a concrete repository storage contract exists.

## Read completeness

A read either proves the end of its traversal or fails. The end is proven only by a provider-documented marker: an empty page, an absent next cursor, or a provider-declared total. A repeated cursor or page, or an exhausted page budget, is not an end: the adapter fails instead of returning the records it saw. `ReadOutcome` records a successful read; an incomplete traversal is never one.

Only a `full` read may justify treating an unseen record as removed (`ReadOutcome.proves_absence`). An `incremental` read returns what changed since a checkpoint; a record it does not return is unchanged, not removed. A consumer applies an incremental read onto an established baseline and never uses it as the baseline itself.

Related data read alongside the records (tax rates, stock levels, names) follows `related_data_may_be_missing`:

- a durable refusal (`authorization`, `entitlement`) lets the read continue, and the read names the data in `ReadOutcome.missing`;
- any other failure, including transient `rate_limit` and `provider_unavailable`, fails the whole read with that failure.

A transient failure reported as missing data would let the consumer overwrite known values with unknown ones at the next full read. Missing data is unknown, never absent: a consumer must not replace a known value with a value from data named in `missing`.

## Rate limits and retries

`429` is classified as `rate_limit` and is retryable. A provider `Retry-After` delay, when represented by the common contract, must be an explicit, finite, non-negative numeric number of seconds (not a boolean or string). The common contract does not invent a retry delay when the provider does not supply one.

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
