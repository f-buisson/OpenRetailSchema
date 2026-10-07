# Adapter selection gate

[POS integration registry](POS_INTEGRATIONS.md) · [Roadmap](ROADMAP.md) · [Contributing](../CONTRIBUTING.md)

OpenRetailSchema does not start a new provider adapter because an API exists. A provider is selected only when the evidence is strong enough to implement the minimum read surface without guessing business semantics and when there is a realistic path to authorized verification.

## Required gates

A future adapter must satisfy all of the following before implementation starts:

1. **Exact provider surface** — the product/edition and current API or export version are identified from official public documentation.
2. **Minimum read fit** — the provider can expose the records needed for at least one declared common read capability without inventing missing values.
3. **Authorized access path** — a legitimate sandbox, test store, API device, eligible subscription or other authorized verification route is known and realistically obtainable.
4. **Execution semantics** — pagination, rate/access limits, historical windows and retry/error boundaries are documented well enough to build bounded reads.
5. **Canonical semantics** — identity, money/currency, tax, timestamps, refunds/returns and absence-vs-zero behavior are either documented or explicitly left unsupported.
6. **Synthetic reproducibility** — wholly fabricated fixtures can exercise the proposed mappings and negative/edge cases without publishing real provider data.
7. **Maintenance cost** — versioning, entitlement variability and provider-specific complexity are bounded enough that the connector can be kept aligned without creating a second common contract.

A provider failing any gate remains **deferred**. Deferred does not mean incompatible; it means evidence or access is insufficient for responsible implementation.

## Current decision — 2026-10-07

**No additional provider adapter is selected.** Square is already the active post-Loyverse implementation and still needs an authorized Sandbox or seller-account run. Starting another adapter before that external proof would add maintenance surface without closing the current commercial/reference path.

| Provider | Documentation | Authorized test path | Canonical-semantic confidence | Maintenance/access cost | Decision | Next proof |
| --- | --- | --- | --- | --- | --- | --- |
| Square | Strong; implementation already synthetic-tested | Sandbox/seller account not yet exercised here | Strong for current product/sale/refund surface; money remains conservative | Moderate | **Continue certification only** | Authorized connector run, kept distinct from OAuth/Marketplace claims |
| Clover | Strong public REST contract; sandbox and OAuth documented | Sandbox exists but has not been exercised here | Good for pagination, timestamps and order boundaries; mappings still synthetic-missing | Moderate | **First re-evaluation candidate after Square** | Authorized sandbox run plus fabricated product/order/payment mappings |
| Lightspeed Retail X-Series | Strong versioned API/scopes/pagination/rate-limit documentation | Authorized test-store access not yet available | Good transport evidence; canonical mappings not yet exercised | Moderate | Deferred | Authorized test store plus fabricated product/sale/outlet/inventory mappings |
| Shopify POS | Strong Admin GraphQL documentation | Development access is plausible but POS-specific proof is absent here | POS-origin discrimination remains unresolved | Moderate to high | Deferred | Official stable POS-origin discriminator plus authorized test evidence |
| Epos Now | V4 products/stock/transactions documented | Requires an API device and device licence | Transaction timezone/offset semantics remain unresolved | Moderate | Deferred | Authorized API-device run plus timestamp semantics and fabricated mappings |
| Odoo POS | JSON-2 documented | Requires an eligible Custom-plan database | Technical model surface varies by database | High | Deferred | Authorized database `/doc` inspection plus fabricated mappings |
| NCR Voyix / StoreLine | Exact public interface not established | No authorized interface established | Unknown | Unknown/high | Deferred | Publicly shareable interface documentation or authorized redacted export specification |

## Re-evaluation rule

Re-evaluate a deferred provider only when new evidence closes one of its named gaps. Do not re-open a provider merely because time passed or because another repository contains an implementation.

When multiple providers become eligible at the same time, prefer the one that:

1. removes duplicated work from downstream retail products;
2. has the strongest authorized test path;
3. fits the existing common connector contract with the fewest provider-only assumptions;
4. has the lowest ongoing version/access maintenance cost.

This decision record changes the order of future implementation only when repository evidence changes.