# Experimental Loyverse read-only transport

[Integration evidence](../../docs/POS_INTEGRATIONS.md) · [Home](../../README.md) · [Official API](https://developer.loyverse.com/docs/)

This experimental Python module is an independent OpenRetailSchema implementation of documented **GET** calls using the official HTTPS Loyverse v1.0 host. It is **not** a certified connector or an adapter that emits canonical records. Other F-Buisson software has successfully exercised a personal token against a real Loyverse account; that test is *separate* and does not certify this code.

Capabilities now available: `merchant()` (raw merchant document) and `iter_collection()` for a fixed allowlist of catalog, store, inventory, tax, receipt, employee, device and shift resources. No write method, OAuth flow, background synchronization, token vault, mapping or persistent RAW storage is provided here.

### Offline validation

```bash
python -m pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
```

The tests inject a fake network transport and fabricated responses. No GitHub Actions are needed.

### Optional manual test (authorized account only)

Do **not** commit real token values or captured JSON payloads. Export `LOYVERSE_API_TOKEN` through your operating system's secret-handling method, never paste it into a public issue. From a local Python shell:

```python
from connectors.loyverse import LoyverseClient, merchant_currency

client = LoyverseClient.from_environment()
merchant = client.merchant()
print("Currency available:", merchant_currency(merchant) is not None)
# Avoid printing the full merchant document or any account identifiers.
```

A personal token has broad access to the associated account. This client only makes read requests but cannot *reduce the token's own permissions*. Use a disposable authorized test token and revoke it after testing; OAuth is the intended multi-merchant deployment model.

HTTP 402 is reported as `plan_restricted_history` rather than prompting a user to replace a valid token. HTTP 429 is reported as `rate_limited`. This module does not silently retry, invent unavailable records, or use a hard-coded historical access window.

### Next steps

Separate source normalization from transport, preserve unknown prices/taxes/inventory, add synthetic fixtures, implement controlled retry/backoff and independent authorized live testing. A StoreLine interface must not be assumed.
