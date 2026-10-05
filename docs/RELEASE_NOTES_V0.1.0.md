# OpenRetailSchema v0.1.0

OpenRetailSchema v0.1.0 is the first tagged experimental foundation release.

## Included

- versioned canonical v0.1 contracts for products, sales and activity metrics;
- explicit source provenance and schema-version semantics;
- decimal-string money rules, currency consistency checks and unknown-vs-zero preservation;
- refund semantics that preserve source signs;
- offset-aware time rules with DST regression coverage;
- generic local product CSV import with explicit mapping and atomic output;
- offline JSON Schema validation and synthetic regression fixtures;
- experimental read-only Loyverse transport with product/sale normalization, pagination, bounded retries and caller-owned incremental checkpoints;
- public POS evidence registry and contribution/security guidance.

## Evidence for the release candidate

On 2026-10-05, a fresh checkout of the candidate was exercised locally with Python 3.13.14:

- 71/71 automated tests passed;
- canonical validator smoke tests passed for product, sale and activity fixtures;
- the documented synthetic product CSV import emitted 3 canonical records with 0 rejected rows;
- a tracked-file secret-pattern scan found no matches;
- no tracked binary/private artifact types were present.

The release-preparation documentation changes are re-tested before the tag is created.

## Experimental boundaries

This release does **not** certify any live POS connector. In particular:

- the OpenRetailSchema Loyverse connector has not yet completed an authorized live connector run;
- OAuth is documented by Loyverse but is not certified by this project;
- no write operation is supported;
- there is no hosted synchronization service, persistent RAW store or token vault;
- canonical Loyverse activity mapping is not implemented;
- StoreLine support is not claimed;
- Square and other POS adapters remain future work.

A separate F-Buisson application has exercised an authorized Loyverse personal-token integration. That evidence informs tests and contracts but does not count as OpenRetailSchema connector certification.

## Compatibility

The 0.1 contract remains experimental. Consumers must inspect `schema_version` and must not silently reinterpret unknown versions as 0.1.0. Breaking pre-1.0 contract changes require a new versioned schema line and documented migration behavior.

## Français — résumé

v0.1.0 publie la première base expérimentale utilisable : contrats canoniques, validation locale, import CSV produit et connecteur Loyverse expérimental testé avec données synthétiques. Cette version **ne certifie pas encore un connecteur POS en conditions réelles** et n'annonce ni OAuth validé, ni écriture POS, ni StoreLine/Square supporté.
