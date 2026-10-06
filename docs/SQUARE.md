# Square connector evidence and boundaries

[Roadmap](ROADMAP.md) · [POS integration registry](POS_INTEGRATIONS.md)

Status: **documented + synthetic implementation merged on `main`**. No live Square account has been used by OpenRetailSchema and no OAuth or Marketplace certification is claimed.

## Official surface reviewed

Reviewed against Square's public API reference on 2026-10-06, API version `2026-09-16` where exposed by the current reference:

- Catalog `GET /v2/catalog/list`: `ITEMS_READ`; cursor pagination; the connector explicitly requests `ITEM,ITEM_VARIATION` rather than relying on version-dependent default object types.
- Orders `POST /v2/orders/search`: `ORDERS_READ`; cursor pagination; at most 10 location IDs per search request. Orders include Square sales and returns, but OpenRetailSchema does not yet normalize them into canonical sales.
- Locations `GET /v2/locations`: `MERCHANT_PROFILE_READ`; used to discover the seller locations required by Orders search.
- Inventory `POST /v2/inventory/counts/batch-retrieve`: `INVENTORY_READ`; cursor pagination and optional filters. Quantities remain provider strings; no missing value is converted to zero.
- Square documents HTTP 429 / `RATE_LIMITED` responses and recommends exponential backoff with jitter. The connector now applies bounded retries to these read operations with injected delays; synthetic tests prove retry bounds and fail-closed exhaustion. This is implementation evidence, not a live quota/certification claim.

Authoritative references:

- https://developer.squareup.com/reference/square/catalog-api/list-catalog
- https://developer.squareup.com/reference/square/orders-api/search-orders
- https://developer.squareup.com/reference/square/locations/list-locations
- https://developer.squareup.com/reference/square/inventory-api/BatchRetrieveInventoryCounts
- https://developer.squareup.com/docs/build-basics/general-considerations/handling-errors

## Authorization, environments and event boundaries

The current read surface needs only the minimum seller permissions that match the operations already implemented:

| Read surface | Minimum Square permission |
| --- | --- |
| catalog / products | `ITEMS_READ` |
| orders / sales source | `ORDERS_READ` |
| locations / stores | `MERCHANT_PROFILE_READ` |
| inventory counts | `INVENTORY_READ` |

For third-party seller accounts, Square OAuth is the normal authorization model: the seller approves requested scopes, Square redirects to the registered callback, and the application exchanges the authorization code for access/refresh tokens. OpenRetailSchema does not implement that OAuth flow yet and therefore does not claim OAuth certification.

Square Sandbox and production are isolated environments with different credentials and resources. Sandbox is free and permits unlimited test API calls. Square notes generically that some production API calls can depend on a seller subscription to the related Square SaaS product; no endpoint-specific paid-plan requirement has been established here for the four read operations above, so this project does not claim one.

Square exposes relevant webhooks such as `catalog.version.updated`, `inventory.count.updated`, `order.created` and `order.updated`. They could support future incremental or near-real-time synchronization, but they are deliberately outside the current bounded read-only connector. Webhook delivery can be duplicated and unordered, so adding them later would require an explicit idempotency/order contract rather than simply wiring event handlers.

Rate-limit evidence is similarly bounded: Square documents `429 RATE_LIMITED` and recommends exponential backoff with jitter. No numeric global request quota is asserted here because the reviewed official material does not establish one for this combined read surface.

Additional authoritative references:

- https://developer.squareup.com/reference/square/o-auth-api
- https://developer.squareup.com/docs/oauth-api/square-permissions
- https://developer.squareup.com/docs/devtools/sandbox/overview
- https://developer.squareup.com/reference/square/enums/ErrorCategory
- https://developer.squareup.com/docs/webhooks/overview
- https://developer.squareup.com/reference/square/catalog-api/webhooks/catalog.version.updated
- https://developer.squareup.com/reference/square/webhooks/inventory.count.updated
- https://developer.squareup.com/reference/square/orders/webhooks

## Current connector boundary

`connectors/square.py` is deliberately transport-injected and read-only. It has no SDK dependency, credentials, persistence, OAuth flow, webhook handling, or write operation. Canonical normalization currently exists only for products; sales, stores and inventory remain provider-level read results until their semantics are defined and tested.

The common operations are mapped as follows:

| Common operation | Square source | Current status |
| --- | --- | --- |
| `products.read` | Catalog list, explicit `ITEM,ITEM_VARIATION` types | synthetic read + conservative canonical product normalization |
| `sales.read` | Locations + Orders search, location IDs chunked to the documented limit of 10 | synthetic implementation |
| `stores.read` | Locations list | synthetic implementation |
| `inventory.read` | Batch retrieve inventory counts | synthetic implementation |

`stores.read`, `sales.read` and `inventory.read` still return provider dictionaries unchanged. `products.read` can be normalized separately with `canonical_square_products()`: `ITEM_VARIATION` is the source identity, parent `ITEM` supplies the canonical name, optional SKU/UPC/deletion state are preserved only when valid, orphan variations fail closed, and `sale_price` is deliberately omitted because integer minor units are not converted without explicit currency-exponent semantics.

## Safety and evidence rules

Tests use fabricated responses only. Provider error details are not echoed by the connector exception. Cursor type, page bounds, retry exhaustion, malformed product fields and orphan variations fail closed. PR #24 merged after the public test workflow passed on its exact head. A future live test must use an authorized Square sandbox or seller account and record only non-sensitive evidence.
