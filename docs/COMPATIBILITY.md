# Schema compatibility policy

[Home](../README.md) · [Architecture](ARCHITECTURE.md) · [Roadmap](ROADMAP.md)

OpenRetailSchema uses explicit semantic versions in every canonical record. The current contract is **0.1.0** and remains experimental until the first tagged release. This document defines how changes are classified so consumers can decide whether to accept a newer contract deliberately rather than by accident.

## Compatibility rules

Within a released minor line, a patch release may:

- clarify descriptions and examples without changing validation;
- add synthetic invalid fixtures or stricter implementation tests for behavior already required by the written contract;
- fix tooling bugs that do not make a previously valid canonical record invalid.

A patch release must **not** add a required field, remove or rename a field, narrow an enum or pattern, change the meaning or units of a field, or reinterpret absence as zero/null. Those changes require a new minor version while the project is pre-1.0.

A new pre-1.0 minor version may make contract changes, but it must have a separate versioned schema directory and migration notes. Existing versioned schemas stay available so consumers can continue validating historical records.

## Consumer rules

Consumers must inspect `schema_version`; they must not silently treat an unknown version as `0.1.0`. Producers must emit the version they actually validate against. Vendor connector versions are separate from schema versions.

Unknown source data stays unknown. In particular:

- an omitted `sale_price` is not a zero price;
- an omitted tax amount or rate is not tax-free;
- an omitted stock quantity is not zero stock;
- a refund is identified by `sale_kind: "refund"`; connectors must preserve the source sign convention rather than inventing a negative sign;
- timestamps are RFC 3339 date-times with an offset or `Z`; local wall-clock strings without an offset are not canonical event timestamps.

Money is a decimal string plus a three-letter uppercase currency code. The current schema does not define whether a vendor's multiple money representations are shop, settlement or presentment currency; a connector must not collapse those concepts unless the mapping is documented and lossless.

## Cross-field semantics

JSON Schema validates record shape and field formats. Some invariants require normalizer or consumer checks and are not yet enforced by `record.schema.json`:

- `activity_metric.interval_end` should be later than `interval_start`;
- `store_timezone`, when supplied, should be an IANA timezone name and should agree with the intended store context;
- line totals and record totals are source facts, not values OpenRetailSchema automatically recomputes;
- tax-inclusive versus tax-exclusive basis is not inferred;
- multiple currencies in one source transaction require an explicit future contract rather than silent conversion.

These gaps are tracked as contract work, not treated as permission to guess.

## Deprecation and migration

Before a stable 1.0 release, incompatible changes are expected to be uncommon but possible. Each incompatible version must document: the old field or behavior, the new representation, whether conversion is lossless, and a deterministic migration example where one exists.

After 1.0, backward-compatible additions belong in minor releases and breaking contract changes require a new major version.

## Connector evidence is independent

Schema compatibility does not certify a POS connector. A connector is only supported after its own authorized end-to-end test. Public vendor documentation, tests in another application, synthetic repository tests and a live OpenRetailSchema connector test remain separate evidence levels.
