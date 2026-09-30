# Security policy

This project is in early development and does not yet provide a production-ready synchronization service.

- Never commit real POS credentials, API keys, customer records, private vendor payloads or production exports.
- Use synthetic test fixtures and separate local configuration from committed files.
- Keep future connector credentials outside source control; use minimal scopes and do not log secrets.
- Treat raw-data storage, retention, store separation and privacy requirements as design and review gates.

To report a security concern, contact [contact@f-buisson.com](mailto:contact@f-buisson.com). Do not disclose exploitable vulnerabilities or personal data in a public issue. Do not send production secrets in the report.
