# Public POS implementation and test-data references

[Home](../README.md) · [POS capability registry](POS_INTEGRATIONS.md) · [Contributing](../CONTRIBUTING.md)

Research snapshot: **2026-09-30**. This is a curated study list, **not** a registry of certified OpenRetailSchema integrations. Review upstream updates and the license of each file before incorporating anything. The canonical OpenRetailSchema specification remains independently maintained under Apache-2.0.

## Independently inspectable implementation references

| Source | What it demonstrates | License / use constraints | What it does **not** prove |
| --- | --- | --- | --- |
| [Pashkevich Loyverse PHP SDK](https://github.com/siarheipashkevich/loyverse-sdk) ([tests](https://github.com/siarheipashkevich/loyverse-sdk/tree/master/tests)) | API resource coverage and mocked HTTP response/error unit tests; PHP SDK includes catalog, receipts, employees, inventory and more. | MIT. Refer to the upstream license and retain applicable notices for any reused code. | Passing mock tests does not establish current live-account access or certify this project's connector. |
| [matteobe Loyverse Python wrapper](https://github.com/matteobe/loyverse) ([receipt tests](https://github.com/matteobe/loyverse/blob/master/tests/test_receipts.py)) | Historical Python receipt/date handling; the tests use VCR-style recorded-request markers. | MIT, but last known updates date to 2020; reassess against current official API. Do **not** import recorded request cassettes or real-looking receipt identifiers. | Old recorded tests do not guarantee present-day provider behavior or authorization. |
| [Square official TypeScript SDK](https://github.com/square/square-nodejs-sdk) | Current vendor-maintained client models, serialization, errors and examples across Square APIs. | MIT at the time of research; maintain upstream attribution if incorporating permissibly licensed pieces. Prefer using it as a dependency/reference rather than copying generated sources. | An SDK is not an OpenRetailSchema normalization adapter or a live compatibility certification. |
| [Square official sample integrations](https://github.com/square/connect-api-examples) | OAuth and sandbox workflows. Relevant individual examples carry Apache-2.0 notices; inspect the actual files used. | Check **per-example** licensing, since the repository has no clearly identified root-level SPDX license. | Samples may target old APIs and still require independently verified permissions. |
| [Unofficial Lightspeed SDK](https://github.com/darrylmorley/lightspeed-retail-sdk) | Existing JavaScript tests and request patterns for a **particular Lightspeed retail API version**. | MIT. Verify the exact product/edition and current endpoint definitions; Lightspeed products are not interchangeable. | A single product SDK does not imply coverage of all Lightspeed Retail/Restaurant APIs. |

Official vendor documentation remains the authoritative reference, even when an open-source SDK is useful. For Loyverse, prefer [official API reference and Postman collection](https://developer.loyverse.com/docs/). The collection is a reference to test against **your own authorized account**, not permission to redistribute API data.

## Tested connector designs to study, not copy

| Source | Available evidence | Restriction |
| --- | --- | --- |
| [Airbyte Square connector](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-square) | Public low-code manifest, order-cursor mock regression tests, integration-test configuration and expected record files. Its published metadata declares live, unit and acceptance-test suites. | **ELv2** in `metadata.yaml`: do **not** copy source, manifest, fixtures or test code into an Apache-2.0 repository without explicit rights review. Examine architecture and *independently* write tests from official Square documentation. Declared tests are not proof of a currently passing live run. |
| [Airbyte Shopify connector](https://github.com/airbytehq/airbyte/tree/master/airbyte-integrations/connectors/source-shopify) | Public GraphQL/bulk-stream implementation, state and rate-limit tests, acceptance-test setup; metadata describes a generally available connector. | **ELv2** in `metadata.yaml`. Study concepts only, write new fixtures and mappings; Shopify Admin data does not automatically prove POS-specific provenance. |

**Never import third-party `expected_records.jsonl` blindly.** Public test outputs may contain account-specific records and customer-like fields, and publicly visible does not mean safe or licensed for republication. Generate new wholly synthetic records.

## Synthetic retail data for load and edge-case tests

- [Retail Data Generator](https://github.com/tharun-reddy-8118/retail-data-generator): MIT-licensed Python/Faker project for fictional customers, products, orders, order items, payments, shipments and returns.
- [ERP Synthetic Data Generator](https://github.com/scripts-and-tables/erp-synthetic-data-generator): MIT-licensed generator with reproducible retail/ERP sales and line items, seasonality and returns.

Both can help **stress-test our normalization pipeline and generic CSV importer** after independent validation. Their generated fields are **not authentic POS API responses**; convert them through explicitly documented test adapters instead of claiming vendor compatibility.

## OpenRetailSchema acceptance evidence model

For every future POS connector, keep evidence at four separate levels:

1. **Documented:** official URL/version, resource fields, authentication, subscription scopes, pagination, timezones and error codes.
2. **Offline reproducible:** a handcrafted fake-response test set covering missing prices and taxes, decimals, refunds, out-of-order timestamps, pagination, HTTP 402/429 and unknown currencies where relevant.
3. **Authorized live test:** date, tested operations, anonymized counts, observed limitations and a verified revocation/disconnection path. Never publish token, original raw payloads or customer identifiers.
4. **Certified OpenRetailSchema mapping:** each tested vendor response produces a schema-valid canonical record with provenance, no inferred unknowns, stable IDs and documented gaps.

Reference implementations should have a clear license compatible with Apache-2.0, but prefer original adapters and synthetic fixtures written expressly for this project. Neither existing source code nor a public CI configuration has been imported from the projects listed above. OpenRetailSchema's own public `Tests` workflow checks repository regressions on pull requests and `main`; it does not turn third-party examples or documentation into live-provider certification.
