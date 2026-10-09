# Square connector evidence and boundaries

[Roadmap](ROADMAP.md) · [POS integration registry](POS_INTEGRATIONS.md)

Status: **documented + synthetic implementation merged on `main`**. No live Square account has been used by OpenRetailSchema and no OAuth or Marketplace certification is claimed.

## Official surface reviewed

Reviewed against Square's public API reference on 2026-10-06, API version `2026-09-16` where exposed by the current reference:

- Catalog `GET /v2/catalog/list`: `ITEMS_READ`; cursor pagination; the connector explicitly requests `ITEM,ITEM_VARIATION` rather than relying on version-dependent default object types.
- Orders `POST /v2/orders/search`: `ORDERS_READ`; cursor pagination; at most 10 location IDs per search request. The read operation returns provider orders; separate conservative mappers normalize completed sales and unambiguous refunds with explicit unsupported fields.
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

`connectors/square.py` is deliberately transport-injected and read-only. It has no SDK dependency, credentials, persistence, OAuth flow, webhook handling, or write operation. Read operations return provider dictionaries; separate tested mappers provide conservative canonical products, completed sales and unambiguous refunds. Stores and inventory do not have canonical mappers.

The common operations are mapped as follows:

| Common operation | Square source | Current status |
| --- | --- | --- |
| `products.read` | Catalog list, explicit `ITEM,ITEM_VARIATION` types | synthetic read + conservative canonical product normalization |
| `sales.read` | Locations + Orders search, location IDs chunked to the documented limit of 10 | synthetic implementation |
| `stores.read` | Locations list | synthetic implementation |
| `inventory.read` | Batch retrieve inventory counts | synthetic implementation |

For `sales.read`, every returned Locations entry is validated before any
Orders search request is sent. Non-object entries, invalid/blank location IDs
and duplicate IDs (including across pages) fail with sanitized errors.
An explicitly empty Locations list retains the existing empty result; this
does not certify provider completeness. IDs keep order and ten-ID batching.

`stores.read`, `sales.read` and `inventory.read` still return provider dictionaries unchanged. `products.read` can be normalized separately with `canonical_square_products()`: `ITEM_VARIATION` is the source identity, parent `ITEM` supplies the canonical name, optional SKU/UPC/deletion state are preserved only when valid, orphan variations fail closed, and `sale_price` is emitted only where Square's pricing semantics are unambiguous.

## Pagination integrity

Both GET and POST paginated read operations reject a cursor already encountered
within the same traversal with `square_cursor_repeated`. A repeated cursor is
not treated as an additional page and its value is never included in errors.
Malformed non-string cursors (including falsy numeric or boolean values) fail
closed with `square_cursor_must_be_string`; missing, null and empty-string
cursors retain the existing end-of-pagination behavior. Each traversal has its
own cursor history. The existing page budget and bounded read retries are
unchanged, but the budget is no longer what ends a cycle: a repeat is refused
on the page that repeats it, so the budget now only bounds a traversal whose
cursors all differ. This behavior is verified only with synthetic responses; it
does not establish live Square connector certification.

## Canonical product price boundary

`CatalogItemVariation.price_money` is converted to canonical `sale_price` only
under the conditions Square documents explicitly:

- `pricing_type` `FIXED_PRICING` with a `price_money` object yields canonical
  `sale_price`; an explicit zero amount is preserved as zero;
- a missing `price_money` leaves `sale_price` absent, and absence is never
  rewritten as zero;
- `pricing_type` `VARIABLE_PRICING` carrying a `price_money` fails closed rather
  than being published as a fixed price, and any other `pricing_type` value fails
  closed as well;
- minor units are converted through one implementation using documented currency
  exponents: `AUD`, `CAD`, `EUR`, `GBP` and `USD` use exponent 2, `JPY` uses
  exponent 0. Any other currency fails closed instead of assuming an exponent;
- the amount must be a JSON integer. A boolean, a float or a missing amount fails
  closed, and a negative amount fails closed because a negative product price is
  not a documented Square meaning even though the canonical money pattern would
  accept the sign.

The conversion is intentionally local to this connector: Square is the only
reviewed provider that publishes integer minor units, so no shared money
abstraction is introduced for a single caller.

## Canonical completed-sale boundary

The canonical sale mapper is intentionally narrower than the raw `sales.read` transport:

- only orders whose Square state is `COMPLETED` are emitted;
- the canonical occurrence time is Square `closed_at`, the documented terminal-state timestamp;
- each emitted line requires a Square line `uid`, `catalog_object_id` (CatalogItemVariation) and positive decimal `quantity`;
- order and line money fields are not emitted yet; the minor-unit conversion is defined and proven for product prices, but mapping order-level and line-level money is outside this lot;
- an order carrying a non-empty `returns` collection fails closed instead of being mislabeled as a pure sale.

This last boundary is deliberate. Square `OrderReturn` provides return itemization but no return-event timestamp of its own, while canonical v0.1 refunds require `occurred_at`. The parent order's `updated_at` is not substituted because that would turn a generic last-modified timestamp into an invented refund occurrence time. A later refund lot must establish an authoritative event-time source and itemization link before `sale_kind: refund` is emitted.

## Canonical refund boundary

Square refund normalization combines two official read models instead of guessing from a generic order modification time. A completed PaymentRefund provides created_at and order_id; the linked refund Order provides OrderReturn.return_line_items, including source_line_item_uid, CatalogItemVariation identity and quantity. Only a one-to-one completed PaymentRefund-to-refund-order link is emitted. Multiple completed refunds linked to the same return order fail closed because item-level allocation would otherwise be invented. Monetary values remain absent: the minor-unit conversion exists for product prices, but refund money mapping is outside this lot.

Authoritative references:

- https://developer.squareup.com/reference/square/refunds-api/list-payment-refunds
- https://developer.squareup.com/docs/refunds-api/retrieve-refunds
- https://developer.squareup.com/reference/square/objects/OrderReturnLineItem

## Safety and evidence rules

Tests use fabricated responses only. Provider error details are not echoed by the connector exception. Cursor type, page bounds, retry exhaustion, malformed product fields and orphan variations fail closed. PR #24 merged after the public test workflow passed on its exact head. A future live test must use an authorized Square sandbox or seller account and record only non-sensitive evidence.
