# OpenRetailSchema

[Français](docs/fr/README.md) · [POS integrations](docs/POS_INTEGRATIONS.md) · [Project roadmap](docs/ROADMAP.md) · [Contributing](CONTRIBUTING.md) · [Apache 2.0](LICENSE)

**Open, vendor-neutral retail data models and an extensible foundation for point-of-sale integrations.**

OpenRetailSchema aims to make it easier for applications to work with different POS systems without implementing a separate data model for every vendor. The project defines canonical contracts, preserves source provenance, and provides room for independent, capability-based connectors.

> **Status: early development.** The initial schemas are a starting contract, not a claim of production readiness. An authorized Loyverse personal-token catalog integration **has been tested in a separate F-Buisson product**, but no live OpenRetailSchema POS connector is certified yet. [See the exact evidence and integration registry.](docs/POS_INTEGRATIONS.md)

## What belongs here

- **Canonical data contracts:** common representations of stores, products, sales, line items, monetary amounts, and transaction provenance. Further domains will be added incrementally.
- **Validation and test fixtures:** vendor-independent examples, locally executable tests, and explicit schema versions.
- **Connector contracts:** a POS advertises exactly which reads, events, or writes it supports; missing fields are never silently invented.
- **Normalization:** source-specific mapping with preserved identifiers, timestamps, precision, and raw-data references.

OpenRetailSchema is an independent open-source project, designed to support any application—not exclusively F-Buisson products. Potential downstream uses include checkout workforce planning, price auditing, and order preparation.

## Design rules

1. **Source integrity:** record the provider and source identifier for each normalized record; never invent absent quantities or prices.
2. **Money and time:** decimal money as strings with ISO currency codes; timestamps use ISO 8601 offsets or UTC, with an explicit store timezone where applicable.
3. **Read-only first:** begin with imports; POS writes require separate capability declarations, safeguards, and tests.
4. **Loss is explicit:** preserve unrecognized vendor attributes separately, and distinguish unavailable, null, and zero when the data model requires it.
5. **Versioned contracts:** maintain machine-readable schema versions and document incompatible changes before releasing them.
6. **Privacy by default:** use synthetic fixtures. Never commit customer data, tokens, credentials, or private vendor payloads.

## Scope and priorities

| Stage | Focus | Status |
| --- | --- | --- |
| Foundation | Public specification, schemas, fixtures, local validation | **v0.1.0 published — experimental** |
| Generic import | Local product CSV adapter with explicit mapping, canonical validation, atomic output and synthetic tests | Experimental; products only |
| Loyverse | Experimental Python read-only client and synthetic tests; independently validate against an authorized live account and assess OAuth | Experimental |
| StoreLine | Adapter only for an interface whose availability and authorization have been verified | Research |
| Ecosystem | SDKs, optional service API, community connectors | Future |

See the [roadmap](docs/ROADMAP.md) for acceptance criteria. A POS is only listed as **supported** after real integration tests; naming a vendor above does not imply compatibility today.

## Quick start

From a fresh checkout with Python 3.10+:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py examples/valid_product.json examples/valid_sale.json examples/valid_activity_metric.json
python -m unittest discover -s tests -v
```

For the generic product CSV example, create a local ignored output directory and run:

```bash
mkdir local-data
python scripts/import_csv.py --input examples/csv/products.csv --mapping examples/csv/products_mapping.json --output local-data/imported-products.jsonl
```

The CSV example is synthetic. The Loyverse connector remains experimental until an authorized live OpenRetailSchema run is recorded.

## Documentation

- [French overview / Présentation en français](docs/fr/README.md)
- [POS integration registry, tested evidence and contribution requests](docs/POS_INTEGRATIONS.md)
- [Experimental Loyverse token transport](connectors/README.md)
- [Local product CSV importer with reproducible example](docs/CSV_IMPORT.md)
- [Guide CSV en français](docs/fr/CSV.md)
- [French POS contribution overview / Intégrations POS en français](docs/fr/POS.md)
- [Architecture and source-data principles](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](CONTRIBUTING.md)

## Community and security

**Help us support other POS systems:** [propose an integration](https://github.com/f-buisson/OpenRetailSchema/issues/new/choose) and share public API documentation, verified capabilities and fabricated sample responses. Square, Shopify, Lightspeed, StoreLine export formats and other vendors are all welcome; see the [evidence registry](docs/POS_INTEGRATIONS.md). **Do not send credentials or real store exports.**

Issues and pull requests are welcome, particularly schema design reviews and reproducible synthetic vendor samples. See [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a connector. Do not post access tokens or real customer transaction data in issues.

Local validation remains fully supported. The public `Tests` workflow also runs on pull requests and `main` to repeat the unit suite; CI success does not certify live vendor access.

---

Maintained by [F-Buisson](https://f-buisson.com). Licensed under [Apache License 2.0](LICENSE). The project is independent of any POS vendor.
