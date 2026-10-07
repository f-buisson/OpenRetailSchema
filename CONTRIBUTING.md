# Contributing

Thank you for helping make retail data easier to exchange. **English is the canonical language** for specifications, code, public APIs, issues and pull requests. French documentation is welcome when it stays aligned with the English source.

## Help document another POS

We welcome publicly shareable API specifications or authorized export formats from **any** POS system. Use the [POS connector proposal form](https://github.com/f-buisson/OpenRetailSchema/issues/new/choose) and the [integration registry](docs/POS_INTEGRATIONS.md). A useful proposal identifies the exact product/edition, official documentation and read capabilities; authentication, scopes, plan restrictions, pagination, timezones, money/tax semantics and return handling; and small **synthetic** examples. Label unverified claims as unknown, not supported. A public API alone does not imply a tested connector.

Contributing general observations from authorized tests is welcome, but do not copy code from private projects, vendor SDKs, restricted documentation or real provider data. All code and documentation submitted for inclusion should be yours to license under [Apache License 2.0](LICENSE).

## Before proposing a change

- Search existing issues and pull requests; explain the real interoperability problem, expected input and output, and edge cases.
- Keep changes small and independently testable. Document incompatible schema changes explicitly.
- Never post real POS credentials, real customer data, confidential vendor SDKs, or restricted API documentation.
- Prefer synthetic fixtures that demonstrate both supported and missing vendor fields. Identify vendor APIs you can legally access before writing adapters. List what is **documented**, **tested in another product**, and **tested in this repository** separately.
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

Use the repository pull-request template. State the exact provider/product/version when vendor-specific, link the official sources used, and keep evidence levels separate: **documented**, **synthetic-tested**, **externally tested**, and **live-tested in this repository** are not interchangeable.

For contributed code or fixtures, state provenance and licensing clearly. Do not paste or adapt private project source, restricted vendor material, or third-party code unless its license is compatible with Apache-2.0 and the required notices are preserved. When a mapping is uncertain, leave it unsupported or unknown rather than converting absence into zero or inventing timezone, tax, refund, or pagination semantics.

Run the relevant local commands and report exactly what was executed. The public `Tests` workflow also runs on pull requests to `main` and repeats the repository unit suite; a green workflow proves repository regression status only, not live provider access or connector certification.

Report security concerns privately using the contact in [SECURITY.md](SECURITY.md), not a public issue.
