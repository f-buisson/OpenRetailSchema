# POS integration registry

[Home](../README.md) · [Contribute a POS](../CONTRIBUTING.md) · [Public SDKs and test-data research](EXTERNAL_REFERENCES.md) · [Version roadmap](ROADMAP.md) · [Français](fr/POS.md)

**Capability and evidence status are separate.** An official API existing, an API being exercised in another application, and an OpenRetailSchema connector being released are three different claims.

Last reviewed: **2026-10-07**.

| Platform | Public interface evidenced | Independent OpenRetailSchema connector | Next contribution |
| --- | --- | --- | --- |
| [Loyverse](https://developer.loyverse.com/docs/) | REST v1.0, personal tokens and OAuth 2.0. Catalog, inventory, tax, merchant, store and receipt resources are documented. | Synthetic-tested read-only transport, product/receipt normalization, bounded retries and caller-owned incremental checkpoints; not yet validated against a live account. | Sanitized end-to-end mapping run, authorized test-account connector run, then OAuth evaluation. |
| [Square](https://developer.squareup.com/reference/square) | Orders, catalog, inventory and OAuth APIs documented. | Synthetic-tested read-only stores/products/sales/inventory adapter on the shared connector contract; product, completed-sale and unambiguous-refund normalization; no live/Sandbox certification. | Authorized Sandbox or seller-account connector run. |
| [Shopify](https://shopify.dev/docs/api/admin-graphql/latest) | GraphQL Admin API documents products, inventory, locations and orders. New public apps must use GraphQL Admin rather than legacy REST. | None. | Prove a safe POS-origin/order mapping and required scopes before proposing an adapter; do not assume all Admin orders are POS sales. |
| [Lightspeed Retail X-Series](https://x-series-api.lightspeedhq.com/docs/introduction) | Date-versioned HTTP/JSON API with OAuth 2.0 Authorization Code and Plus-plan personal tokens; products, sales, outlets and inventory have explicit read scopes. | None. | Authorized test-store access plus synthetic product/sale/outlet/inventory mappings before proposing an adapter. |
| [Clover](https://docs.clover.com/dev/docs/making-rest-api-calls) | REST API documents inventory, orders and payments; sandbox test tokens and production OAuth are distinct, with explicit read/write permissions. | None. | Authorized sandbox run plus synthetic inventory/order/payment mappings before proposing an adapter. |
| [Odoo](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html) | Odoo 19 JSON-2 is available on Custom plans; bearer API keys, database-specific models/fields/methods and standard access rules apply. | None. | Verify the actual POS model surface from an authorized database `/doc` page and provide synthetic read-only mappings before proposing an adapter. |
| [Epos Now](https://developer.eposnowhq.com/Docs/Authentication) | REST API V4 documents products, product stock and transactions; authentication uses per-API-device Basic tokens derived from an API key/secret. | None. | Authorized API-device run plus verified transaction timezone semantics and synthetic product/stock/sale mappings before proposing an adapter. |
| NCR Voyix / StoreLine | **Not independently verified:** access to one NCR Voyix product does not establish an open StoreLine API or permission to use it. | None. | Publicly shareable integration documentation or an authorized, redacted export specification first. |
| Other POS platforms | Open for proposals. | None. | [Open a POS connector request](https://github.com/f-buisson/OpenRetailSchema/issues/new/choose). |

These references describe vendor platforms, not partnerships or endorsements. No platform except Loyverse has product-test evidence recorded here. Do not merge vendor SDKs or text unless their redistribution terms permit it.

## Shopify evidence review — 2026-10-06

This is a **documentation review only**. No Shopify account, token, payload or OpenRetailSchema connector was exercised.

- New public apps must use the GraphQL Admin API; the REST Admin API is legacy. OpenRetailSchema should therefore avoid starting a new REST adapter.
- GraphQL connections use cursor pagination and allow at most 250 resources per page. Shopify also documents bulk operations for larger datasets; this is a separate execution model and should not be hidden behind ordinary cursor semantics without an explicit contract.
- GraphQL Admin throttling is query-cost based per app/store. The documented restore rate varies by plan (including 100 points/s for Standard and higher rates for higher plans), so a future connector must consume returned throttle/cost state rather than hard-code a request-per-second quota.
- Locations are exposed as a paginated connection and are suitable evidence for a future store/location capability.
- Orders require order-read access. By default only the most recent 60 days are available; older history requires additional all-orders access. That entitlement boundary must be represented explicitly rather than treated as an empty history.
- The public Admin Order surface does **not by itself prove that every order is a Shopify POS transaction**. A future adapter must establish an official, stable POS-origin discriminator before mapping Admin orders to a POS sale stream.

Official sources reviewed: [GraphQL pagination](https://shopify.dev/docs/api/usage/pagination-graphql), [GraphQL Admin rate limits](https://shopify.dev/docs/apps/build/apis/graphql-admin/rate-limits), [bulk operations](https://shopify.dev/docs/apps/build/apis/graphql-admin/bulk-operations/queries), [locations](https://shopify.dev/docs/api/admin-graphql/latest/queries/locations), [Order](https://shopify.dev/docs/api/admin-graphql/latest/objects/Order), and the [legacy REST notice](https://shopify.dev/docs/api/admin-rest/latest/resources/order).

**Adapter decision:** deferred. Documentation quality is sufficient for further design work, but POS-origin semantics and authorized test access are not yet evidenced strongly enough to justify implementation. This avoids creating a generic Shopify-commerce connector while claiming POS interoperability.

## Lightspeed Retail X-Series evidence review — 2026-10-06

This is a **documentation review only**. No Lightspeed account, token, payload or OpenRetailSchema connector was exercised.

- New integrations should target the current date-based API versions; legacy v0.9 and v2.0 are deprecated and no longer receive new features.
- OAuth 2.0 uses the Authorization Code Grant. New authorization requests must include explicit scopes, and the documented read scopes include `products:read`, `sales:read`, `outlets:read`, `inventory:read` and `retailer:read` where applicable.
- Personal tokens are available only to retailers on the Plus plan. Lightspeed recommends OAuth for applications connecting to multiple retailers, so personal-token availability must not be treated as general production access.
- Collection pagination is driven by the monotonically increasing resource `version`: callers advance with the response maximum as the next `after` value and stop on an empty collection. Page-size ceilings can vary by endpoint and must not be hard-coded globally without endpoint evidence.
- Authorized API traffic is rate-limited per retailer/application. The published default budget is `300 × register count + 50` requests per 5-minute window, with `X-RateLimit-Limit` and `X-RateLimit-Remaining` response headers. Authorization/token endpoints have separate limits and can return HTTP 429.
- Product and sales list endpoints are explicitly paginated and require `products:read` and `sales:read` respectively; the scope registry separately documents outlets and inventory reads.

Official sources reviewed: [Introduction](https://x-series-api.lightspeedhq.com/docs/introduction), [Authorization](https://x-series-api.lightspeedhq.com/docs/authorization), [OAuth scopes](https://x-series-api.lightspeedhq.com/v2026.04/docs/scopes), [Pagination](https://x-series-api.lightspeedhq.com/v2026.01/docs/pagination), [Rate limiting](https://x-series-api.lightspeedhq.com/v1.0/docs/rate_limiting), [Products](https://x-series-api.lightspeedhq.com/reference/listproducts), and [Sales](https://x-series-api.lightspeedhq.com/reference/listsales).

**Adapter decision:** deferred pending authorized test-store access and synthetic canonical mapping evidence. The public contract is strong enough to define a future read-only adapter, but documentation alone is not connector certification.

## Clover evidence review — 2026-10-06

This is a **documentation review only**. No Clover account, token, merchant payload or OpenRetailSchema connector was exercised.

- Clover separates sandbox and production credentials. Sandbox test merchants can use merchant-specific test API tokens; production web apps use OAuth, and the current v2/OAuth flow issues expiring access/refresh token pairs.
- Permissions are configured per data category and Read/Write direction. A future read-only adapter must request only the resource reads it actually needs; permission changes can require merchants, including test merchants, to reinstall the app.
- Top-level REST collections use offset/limit pagination. The documented default is 100 records and the hard limit is 1000; nested expanded fields are not pageable and can be truncated to their first 100 records, so a connector must not treat an expanded nested collection as complete without endpoint-specific evidence.
- Published REST limits are 50 new requests/s per app and 16/s per token, plus concurrent limits of 10 per app and 5 per token. HTTP 429 is the rate-limit signal; concurrent-limit responses include `retry-after`, and Clover documents exponential backoff after repeated 429s.
- Clover timestamps are milliseconds since the Unix epoch. They must be converted explicitly; milliseconds must never be interpreted as seconds.
- Order retrieval has entitlement/query-window boundaries. The v3 order reference documents 90-day restrictions for several filtered searches, while Clover recommends time-windowed queries for larger histories. This must be represented as an access/query boundary, not as an empty history.
- Orders can expand payments, refunds and line items, but expanded/nested data inherits the pagination-completeness warning above. A future canonical sale mapper must therefore fetch or prove complete itemization rather than silently accepting truncation.

Official sources reviewed: [REST API usage](https://docs.clover.com/dev/docs/making-rest-api-calls), [v2/OAuth](https://docs.clover.com/dev/docs/use-oauth), [app permissions](https://docs.clover.com/dev/docs/permissions), [sandbox test tokens](https://docs.clover.com/dev/docs/using-api-tokens), [pagination](https://docs.clover.com/dev/docs/paginating-elements), [rate limits](https://docs.clover.com/dev/docs/api-usage-rate-limits), [timestamp conversion](https://docs.clover.com/dev/docs/convert-timestamps-to-unix-time), and [orders](https://docs.clover.com/dev/reference/ordergetorders).

**Adapter decision:** deferred pending authorized sandbox access and synthetic canonical mapping evidence. The public contract is sufficient to design a bounded read-only adapter, but documentation alone is not connector certification.

## Odoo 19 evidence review — 2026-10-07

This is a **documentation review only**. No Odoo database, API key, payload or OpenRetailSchema connector was exercised.

- Odoo 19 introduces the external JSON-2 API at `POST /json/2/<model>/<method>` and authenticates requests with a bearer API key. New OpenRetailSchema work should target JSON-2 rather than start a legacy XML-RPC/JSON-RPC integration; those older RPC endpoints are scheduled for removal in Odoo 22.
- External API data access is available only on the **Custom** Odoo pricing plan, not One App Free or Standard. A future connector must treat plan eligibility as an access prerequisite, never as an empty dataset.
- The actual models, fields and methods exposed by JSON-2 are specific to each database and can be inspected on that database's `/doc` page. OpenRetailSchema must therefore verify the installed Point of Sale model surface on an authorized database before claiming a portable product, sale or inventory mapping.
- JSON-2 uses Odoo's normal access rights, record rules and field access controls. A future read-only integration should use a dedicated service user with only the permissions required by the declared connector capabilities.
- Manually created API keys have explicit lifetimes and cannot last more than three months, so credential rotation is part of the access contract rather than an exceptional recovery path.
- Odoo ORM search operations expose `offset`, `limit` and `order`. A future reader may paginate with bounded offset/limit windows, but it should specify deterministic ordering and must not invent a provider cursor or global page-size ceiling that the documentation does not define.
- Point of Sale product documentation confirms that products, variants and stock are part of the POS domain, but the public external-API contract does not by itself prove a fixed cross-database technical model/field mapping for POS sales.

Official sources reviewed: [External JSON-2 API](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html), [ORM search/read](https://www.odoo.com/documentation/19.0/developer/reference/backend/orm.html), [legacy RPC migration notice](https://www.odoo.com/documentation/19.0/developer/reference/external_rpc_api.html), and [Point of Sale products](https://www.odoo.com/documentation/19.0/applications/sales/point_of_sale/products.html).

**Adapter decision:** deferred pending an authorized Custom-plan database, inspection of its `/doc` model surface and synthetic canonical mappings. Documentation is sufficient to define safe access boundaries, but not to claim a universal Odoo POS schema or connector certification.

## Epos Now evidence review — 2026-10-07

This is a **documentation review only**. No Epos Now account, API device, token, payload or OpenRetailSchema connector was exercised.

- Current integration work should target **API V4** where a V4 equivalent exists. The public V2 product, product-stock, transaction and transaction-item references mark those endpoints deprecated and direct new integrations to V4.
- Authentication uses a Basic authorization token derived by Base64-encoding the API device's key and secret. Tokens differ per registered API device, and API-device credentials can be regenerated in Backoffice. Credentials must therefore be treated as rotating secrets and never published in fixtures or diagnostics.
- Creating an API device consumes an Epos Now device licence. The Backoffice also exposes the account's API request limit. Public documentation does not define one universal numeric quota, so a future connector must not hard-code a global requests-per-second budget; an account-specific `API Limit Exceeded` condition is an access/rate-limit boundary, not an empty result.
- V4 products and product stock expose separate read surfaces. V4 collection reads use page-number pagination with up to **200 records per page**; omitting the page returns page 1. A future reader must bound page traversal and stop from observed page content rather than inventing a cursor.
- V4 transaction documentation exposes latest-transaction paging and transaction records with item, tender, tax and refund-related fields. This is enough to justify further synthetic mapping work, but not enough to claim canonical sale/refund semantics without fixtures and authorized observation.
- The public transaction schema exposes a `DateTime` string, but the reviewed material does not establish a timezone or mandatory UTC offset for that value. OpenRetailSchema must not emit a canonical sale `event_time` from an offsetless provider timestamp until official timezone semantics or authorized evidence establish the conversion.
- V4 token information is tied to the authorizing token and includes application/location context. A single API-device token therefore must not be assumed to prove complete multi-location coverage without authorized testing.

Official sources reviewed: [Authentication](https://developer.eposnowhq.com/Docs/Authentication), [API device setup and limits](https://developer.eposnowhq.com/Setup/ApiDevice), [pagination](https://developer.eposnowhq.com/Docs/Pagination), [V4 reference](https://developer.eposnowhq.com/Docs/v4/index), [V2 products](https://developer.eposnowhq.com/Docs/Api?endpoint=Product), [V2 transactions](https://developer.eposnowhq.com/Docs/Api?endpoint=Transaction), and [transaction model introduction](https://developer.eposnowhq.com/Docs/TransactionIntroduction).

**Adapter decision:** deferred pending an authorized API-device run, explicit transaction timezone/offset evidence and synthetic canonical product/stock/sale mappings. The public V4 surface is promising, but documentation alone is not connector certification and does not justify guessing event-time semantics.

## Loyverse capability declaration

This table describes the connector code currently present in this repository. **Synthetic-tested** means fabricated responses exercise repository behavior; it does not mean the OpenRetailSchema connector has been run against a live Loyverse account.

| Capability | Current support | Evidence / boundary |
| --- | --- | --- |
| Merchant read | Supported, GET-only | `merchant()` returns the raw merchant object; synthetic transport behavior only. |
| Raw collection reads | Supported, GET-only for `items`, `variants`, `inventory`, `taxes`, `stores`, `receipts`, `employees`, `pos_devices`, and `shifts` | Allowlisted by `_COLLECTIONS`; raw availability is not canonical emission. |
| Pagination | Supported | Cursor pagination has bounded page count, cursor validation and synthetic tests. |
| Canonical product emission | Supported from variant input | `canonical_product()` emits canonical v0.1 `product`; synthetic-tested. |
| Canonical sale emission | Supported from receipt input | `canonical_sale()` emits canonical v0.1 `sale`; synthetic-tested. |
| Canonical activity emission | Unsupported | No activity mapper exists; shifts/receipts/sessions are not inferred into activity. |
| Write operations | Unsupported | The connector exposes no create/update/delete operation. |
| Bounded retries | Supported for GET only | Finite 1..5-attempt budget (default 3); connection failures, HTTP 429 and provider 5xx are retryable. 401/402/403 and other permanent client errors fail immediately. `Retry-After` accepts only finite 0..5-second deltas. Synthetic-tested; not live-certified. |
| Incremental checkpoints | Supported, caller-owned | `read_incremental()` accepts and returns an explicit-offset `updated_at` source marker, sends it as `updated_at_min`, and advances monotonically only after complete traversal and processing. Missing, null, malformed or offsetless update times are rejected rather than converted to zero/epoch. Pagination cursors remain ephemeral transport state. Synthetic-tested; no persistence or live certification is claimed. |
| Live OpenRetailSchema connector certification | Not tested | Authorized live connector run remains a P2 requirement. |
| OAuth certification | Not tested | OAuth is vendor-documented, but this connector has not independently exercised it. |

## Loyverse canonical mapping boundary

The current connector emits only two canonical v0.1 entity types: **product** from variant data and **sale** from receipt data. Both paths are covered by fabricated schema-validation tests and fail closed when required source identity or other required mapping inputs are malformed. Optional monetary values remain absent when the source value or currency cannot be represented safely; explicit numeric zero remains zero.

The transport can read additional documented collections, including `shifts`, but raw collection availability is not a canonical mapping claim. OpenRetailSchema currently emits **no canonical activity record from Loyverse**. A shift, receipt stream or POS session is not assumed to represent the canonical aggregated activity interval without a documented, semantically sufficient mapping for the required activity fields. Activity therefore remains explicitly unsupported by this adapter rather than being fabricated by inference.

Likewise, transport support for items, inventory, taxes, stores, employees, POS devices or shifts does not mean those resources are normalized into canonical records. Only the product and sale mappers above are part of the current canonical emission surface. This boundary is synthetic-tested repository behavior, not live connector certification.

## Evidence: existing Loyverse token integration

A separate F-Buisson retail application was exercised against a **real Loyverse account**, using a temporary personal access token **exclusively for read operations** (the token itself was high-privilege), on **2026-09-29**. The exercised resources were `/variants`, `/items`, `/inventory`, `/taxes`, `/stores` and `/merchant`. The test read 43 products and 43 variants and confirmed that catalog sync and incremental re-reading work. This is **evidence that a token-based Loyverse API connection works**, not a claim that the connector in this repository has already been certified or that the vendor endorses this project.

Crucial observed behaviors that OpenRetailSchema must preserve in regression tests:

- 10 product prices and 42 stock readings were unavailable; they remained **unknown**, never zero.
- No tax was configured. The taxable basis and rates remained **unknown**; no default VAT rate was inferred.
- `merchant.currency` was returned as an object containing a currency code on the tested account (THB), not necessarily a bare string. Never default a missing or unparsable source currency to EUR in canonical records.
- Repeated incremental catalog reads produced no duplicates.
- Historical receipts access on this test account could return **HTTP 402** beyond its entitled history window. This does **not** mean invalid credentials. The boundary changes over time; do not hard-code a 31-day guarantee.
- A separate receipt normalization experiment used 44 source receipts (including two refunds), but that experiment does **not** establish a production-ready OpenRetailSchema receipts connector. The project's own end-to-end test remains pending.

The test account, full vendor payloads, original source code and tokens are **not published**. Only generalized observations and **synthetic fixtures** may enter this repository. The same distinction applies to prototypes or separate integrations used for PlanCaisse and other applications: their tests inform the contract; they do not count as this repository's release certification.

## Official Loyverse API and access model

Authoritative documentation: [Loyverse API reference](https://developer.loyverse.com/docs/). The documented base URL is `https://api.loyverse.com/v1.0`. Both personal access tokens and OAuth 2.0 are documented. Treat personal tokens as high-privilege credentials; never place them in source, issue reports, public fixtures or application logs. For multi-merchant applications, OAuth with appropriately requested read capabilities is the target; a successful personal-token test does not validate an OAuth integration.

Capabilities are **per operation**, never a generic “compatible” score. An API endpoint appearing in vendor documentation must not be labelled tested until exercised against an authorized account. A platform's plan, scopes and account configuration can affect what can actually be read.

## Contribute another POS integration

The most useful initial contributions are **public facts**, not proprietary code: the official API URL/version; read-only authentication options and required permissions; resource/field mapping for products, prices, tax treatment, stores, transactions, refunds and stock; pagination and quotas; timezones and timestamp semantics; entitlement/plan limitations; and a license-safe, fully synthetic minimal response with a corresponding expected canonical record.

Contributors may also propose a **CSV export mapping** when the POS has no accessible API. Mark fields as *available*, *conditionally available*, *not provided*, or *unknown*. Never infer employee schedules or customer counts from cash sessions or receipts.

**Do not share personal tokens, client secrets, account IDs, real customer or employee information, private documentation, or unredacted exports.** If you have an integration you cannot publicly document, describe its capabilities at a high level and contact the maintainer privately for an authorization discussion.

See [CONTRIBUTING.md](../CONTRIBUTING.md) and the [POS connector issue form](../.github/ISSUE_TEMPLATE/pos-connector.yml).
