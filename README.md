# OpenRetailSchema

[Français](docs/fr/README.md) · [Project roadmap](docs/ROADMAP.md) · [Contributing](CONTRIBUTING.md)

**Open, vendor-neutral retail data models and an extensible foundation for point-of-sale integrations.**

OpenRetailSchema aims to make it easier for applications to work with different POS systems without implementing a separate data model for every vendor. The project defines canonical contracts, preserves source provenance, and provides room for independent, capability-based connectors.

> **Status: early development.** The initial schemas are a starting contract, not a claim of production readiness. No live POS integration is certified yet.

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
| Foundation | Public specification, schemas, fixtures, local validation | In progress |
| Generic import | Configurable CSV mapping, deterministic normalization | Planned |
| Loyverse | Read-only connector with documented capabilities and safe incremental synchronization | Planned |
| StoreLine | Adapter only for an interface whose availability and authorization have been verified | Research |
| Ecosystem | SDKs, optional service API, community connectors | Future |

See the [roadmap](docs/ROADMAP.md) for acceptance criteria. A POS is only listed as **supported** after real integration tests; naming a vendor above does not imply compatibility today.

## Documentation

- [French overview / Présentation en français](docs/fr/README.md)
- [Architecture and source-data principles](docs/ARCHITECTURE.md)
- [Roadmap](docs/ROADMAP.md)
- [Contributing](CONTRIBUTING.md)

## Community and security

Issues and pull requests are welcome, particularly schema design reviews and reproducible synthetic vendor samples. See [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a connector. Do not post access tokens or real customer transaction data in issues.

This repository does not require GitHub Actions. Validation may be run locally without any hosted CI service.

---

Maintained by [F-Buisson](https://f-buisson.com). The project is independent of any POS vendor.
