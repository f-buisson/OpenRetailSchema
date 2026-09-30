# Contributing

Thank you for helping make retail data easier to exchange. **English is the canonical language** for specifications, code, public APIs, issues and pull requests. French documentation is welcome when it stays aligned with the English source.

## Before proposing a change

- Search existing issues and pull requests; explain the real interoperability problem, expected input and output, and edge cases.
- Keep changes small and independently testable. Document incompatible schema changes explicitly.
- Never post real POS credentials, real customer data, confidential vendor SDKs, or restricted API documentation.
- Prefer synthetic fixtures that demonstrate both supported and missing vendor fields. Identify vendor APIs you can legally access before writing adapters.
- Do not claim that a POS integration is supported without an end-to-end authorized test.

## Local verification

Install Python 3.10+ and run:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/valid_sale.json examples/valid_product.json examples/valid_activity_metric.json
python -m unittest discover -s tests -v
```

Add at least one regression fixture for behavior changes. Avoid writing vendor-specific assumptions into the common schema when namespaced `extensions` or connector mappings can model them.

## Pull requests

Describe what changed, why it is necessary, which schema version it affects, what was tested locally, and any missing vendor capabilities or security implications. Maintainers may request evidence or tests before accepting an integration.

No hosted GitHub Actions are configured for this project. Local validation is the reference process until an explicitly approved CI policy exists.

Report security concerns privately using the contact in [SECURITY.md](SECURITY.md), not a public issue.
