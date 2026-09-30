# POS integration registry

[Home](../README.md) · [Contribute a POS](../CONTRIBUTING.md) · [Version roadmap](ROADMAP.md) · [Français](fr/POS.md)

**Capability and evidence status are separate.** An official API existing, an API being exercised in another application, and an OpenRetailSchema connector being released are three different claims.

Last reviewed: **2026-09-30**.

| Platform | Public interface evidenced | Independent OpenRetailSchema connector | Next contribution |
| --- | --- | --- | --- |
| [Loyverse](https://developer.loyverse.com/docs/) | REST v1.0, personal tokens and OAuth 2.0. Catalog, inventory, tax, merchant, store and receipt resources are documented. | Not yet validated against a live account. Read-only token access has been exercised successfully in a separate F-Buisson application (details below). | Independent token test against an authorized **test** account, synthetic pagination/402/429 fixtures, then OAuth evaluation. |
| [Square](https://developer.squareup.com/reference/square) | Orders, catalog, inventory and OAuth APIs documented. | None. | A documented read-only capability proposal and synthetic orders/catalog fixtures. |
| [Shopify](https://shopify.dev/docs/api/admin-graphql/latest) | GraphQL Admin APIs document products, inventory and orders; Shopify POS-specific behavior must be validated independently. | None. | GraphQL read scopes, POS-origin filters, pagination, synthetic examples. |
| [Lightspeed Retail X-Series](https://x-series-api.lightspeedhq.com/docs/introduction) | HTTP API with OAuth and personal tokens; the latter have plan restrictions. | None. | A read-only capability matrix, rate-limit handling and sanitized fixtures. |
| [Clover](https://docs.clover.com/dev/docs/making-rest-api-calls) | REST API documents inventory, orders and payments; test-merchant sandbox and OAuth are available. | None. | Synthetic inventory/order payloads, permissions and time-unit mapping. |
| [Odoo](https://www.odoo.com/documentation/19.0/developer/reference/external_api.html) | Odoo 19 documents the external JSON-2 API, subject to **Custom-plan access**; exact POS models vary by database. | None. | Validate accessible POS models and provide synthetic export mappings. |
| [Epos Now](https://developer.eposnowhq.com/Docs/Authentication) | Official developer documentation describes API-key/secret authentication for an API device. | None. | Public product/order endpoints, access requirements, security behavior and synthetic exports. |
| NCR Voyix / StoreLine | **Not independently verified:** access to one NCR Voyix product does not establish an open StoreLine API or permission to use it. | None. | Publicly shareable integration documentation or an authorized, redacted export specification first. |
| Other POS platforms | Open for proposals. | None. | [Open a POS connector request](https://github.com/f-buisson/OpenRetailSchema/issues/new/choose). |

These references describe vendor platforms, not partnerships or endorsements. No platform except Loyverse has product-test evidence recorded here. Do not merge vendor SDKs or text unless their redistribution terms permit it.

## Evidence: existing Loyverse token integration

A separate F-Buisson retail application was exercised against a **real Loyverse account**, using a temporary personal access token **exclusively for read operations** (the token itself was high-privilege), on **2026-09-29**. The exercised resources were `/variants`, `/items`, `/inventory`, `/taxes`, `/stores` and `/merchant`. The test read 43 products and 43 variants and confirmed that catalog sync and incremental re-reading work. This is **evidence that a token-based Loyverse API connection works**, not a claim that the connector in this repository has already been certified or that the vendor endorses this project.

Crucial observed behaviors that OpenRetailSchema must preserve in regression tests:

- 10 product prices and 42 stock readings were unavailable; they remained **unknown**, never zero.
- No tax was configured. The taxable basis and rates remained **unknown**; no default VAT rate was inferred.
- `merchant.currency` was returned as an object with a currency code on the tested account (THB), not necessarily a bare string. Never default a missing or unparsable source currency to EUR in canonical records.
- Repeated incremental catalog reads produced no duplicates.
- Historical receipts access on this test account could return **HTTP 402** beyond its entitled history window. This does **not** mean invalid credentials. The boundary changes over time; do not hard-code a 31-day guarantee.
- A separate receipt normalization experiment used 44 source receipts (including two refunds), but that experiment does **not** establish a production-ready OpenRetailSchema receipts connector. The project's own end-to-end test remains pending.

The test account, full vendor payloads, original source code and tokens are **not** published. Only generalized observations and **synthetic fixtures** may enter this repository. The same distinction applies to prototypes or separate integrations used for PlanCaisse and other applications: their tests inform the contract; they do not count as this repository's release certification.

## Official Loyverse API and access model

Authoritative documentation: [Loyverse API reference](https://developer.loyverse.com/docs/). The documented base URL is `https://api.loyverse.com/v1.0`. Both personal access tokens and OAuth 2.0 are documented. Treat personal tokens as high-privilege credentials; never place them in source, issue reports, public fixtures or application logs. For multi-merchant applications, OAuth with appropriately requested read capabilities is the target; a successful personal-token test does not validate an OAuth integration.

Capabilities are **per operation**, never a generic “compatible” score. An API endpoint appearing in vendor documentation must not be labelled tested until exercised against an authorized account. A platform's plan, scopes and account configuration can affect what can actually be read.

## Contribute another POS integration

The most useful initial contributions are **public facts**, not proprietary code: the official API URL/version; read-only authentication options and required permissions; resource/field mapping for products, prices, tax treatment, stores, transactions, refunds and stock; pagination and quotas; timezones and timestamp semantics; entitlement/plan limitations; and a license-safe, fully synthetic minimal response with a corresponding expected canonical record.

Contributors may also propose a **CSV export mapping** when the POS has no accessible API. Mark fields as *available*, *conditionally available*, *not provided*, or *unknown*. Never infer employee schedules or customer counts from cash sessions or receipts.

**Do not share personal tokens, client secrets, account IDs, real customer or employee information, private documentation, or unredacted exports.** If you have an integration you cannot publicly document, describe its capabilities at a high level and contact the maintainer privately for an authorization discussion.

See [CONTRIBUTING.md](../CONTRIBUTING.md) and the [POS connector issue form](../.github/ISSUE_TEMPLATE/pos-connector.yml).
