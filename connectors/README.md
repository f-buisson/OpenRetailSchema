# Experimental Loyverse read-only connector

[Integration evidence](../docs/POS_INTEGRATIONS.md) · [Home](../README.md) · [Official API](https://developer.loyverse.com/docs/)

This module is an independent OpenRetailSchema implementation of documented **GET** calls against the official Loyverse v1.0 API. It is **experimental**: repository behavior is synthetic-tested, while an authorized live OpenRetailSchema connector run is still required before the project can claim live support.

## Current capabilities

- raw merchant read;
- allowlisted collection reads for catalog, stores, inventory, taxes, receipts, employees, devices and shifts;
- cursor pagination with bounded traversal and repeated-cursor protection;
- canonical v0.1 product normalization from variant input;
- canonical v0.1 sale normalization from receipt input, including refund direction;
- finite retries for retryable GET failures, with bounded `Retry-After`;
- caller-owned incremental checkpoints based on explicit-offset `updated_at` markers;
- fail-closed handling for malformed identifiers, timestamps, money and unsupported values.

The connector does **not** provide writes, persistent synchronization state, a token vault, canonical activity mapping, production OAuth handling or live certification.

## Offline validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

Tests inject fabricated provider responses. They must never contain real account payloads, customer data or credentials.

## Optional authorized manual test

Do **not** commit token values or captured vendor JSON. Export `LOYVERSE_API_TOKEN` using the operating system's secret-handling method and use a disposable authorized test credential that can be revoked afterwards.

```python
from connectors.loyverse import LoyverseClient, merchant_currency

client = LoyverseClient.from_environment()
merchant = client.merchant()
print("Currency available:", merchant_currency(merchant) is not None)
```

Avoid printing the full merchant document or account identifiers. A successful personal-token test remains separate from OAuth certification.

## Evidence boundaries

A separate F-Buisson retail application has exercised a real Loyverse personal-token integration. Those observations inform this repository's contracts and tests, but they do **not** certify this connector. See [the evidence registry](../docs/POS_INTEGRATIONS.md).

## Next steps

1. exercise sanitized end-to-end product and sale mappings;
2. rerun the complete suite from a fresh checkout of the exact release candidate;
3. perform an authorized live OpenRetailSchema connector run and record only non-sensitive evidence;
4. evaluate OAuth independently after the personal-token path is proven;
5. use the resulting capability contract as the reference for future POS adapters.
