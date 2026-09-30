# Security policy

This project is in early development and does not yet provide a production-ready synchronization service.

- Never commit real POS credentials, API keys, customer records, private vendor payloads or production exports.
- Use synthetic test fixtures and separate local configuration from committed files.
- Keep connector credentials outside source control; use minimal scopes where a provider supports them, and do not log secrets. A Loyverse personal access token has broad account privileges **even when the client only sends GET requests**; restrict use to authorized accounts and revoke disposable test tokens promptly.
- The experimental Loyverse transport uses a fixed official HTTPS host and does not follow redirects. It reports HTTP 402 (history entitlement) separately from HTTP 401 (authentication) and HTTP 429 (rate limiting). Do not upload network traces with authorization headers.
- Treat raw-data storage, retention, store separation and privacy requirements as design and review gates.

To report a security concern, contact [contact@f-buisson.com](mailto:contact@f-buisson.com). Do not disclose exploitable vulnerabilities or personal data in a public issue. Do not send production secrets in the report.
