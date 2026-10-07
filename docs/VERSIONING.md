# Versioning and migration guarantees

[Compatibility policy](COMPATIBILITY.md) · [Architecture](ARCHITECTURE.md) · [Roadmap](ROADMAP.md)

OpenRetailSchema has several independent version axes. They must not be collapsed into one number or silently inferred from each other.

## Version axes

### Repository releases

Git tags use Semantic Versioning in the form `vMAJOR.MINOR.PATCH`. A repository release may change documentation, connectors or tooling without changing the canonical schema contract.

The first published repository release is `v0.1.0`. Pre-1.0 releases are experimental, but breaking changes still require an explicit migration boundary rather than silently redefining an existing contract.

### Canonical record schema

Every canonical record carries an exact `schema_version`, currently `0.1.0`. The current schema is stored under `schemas/v0.1/`.

The schema version is independent from the repository release tag. For example, a future repository patch that changes only documentation or connector implementation may continue emitting canonical schema `0.1.0`.

Consumers must fail closed on an unsupported `schema_version`. They must never reinterpret an unknown version as the closest known version. The regression fixture `examples/invalid_product_schema_version.json` locks this behavior for the current validator.

### Connector capability manifest

The generic connector capability contract currently uses `manifest_version: "1"`. It is independent from canonical `schema_version` and repository tags.

A connector-contract change requires a new manifest version when an existing conforming adapter would otherwise need to change only to remain conforming. This includes:

- changing the manifest shape or support-state meaning;
- removing or renaming a common operation;
- adding a new operation to the mandatory `COMMON_READ_OPERATIONS` set;
- changing fail-closed behavior in a way that alters existing caller expectations.

Provider-specific capabilities may be added without a manifest-version change when they do not redefine the common contract.

### Provider API versions

A provider API version such as the Square request version is source metadata. Updating it does not by itself change a canonical schema or connector-manifest version. Any observed semantic change must still be reviewed against the relevant OpenRetailSchema contracts.

## Change classification before 1.0

### Patch repository release

A pre-1.0 patch may include:

- documentation and example clarifications;
- tests for behavior already required by the published contract;
- connector/provider fixes that preserve declared common behavior;
- tooling fixes that do not make a previously valid canonical record invalid.

A patch must not silently redefine canonical field meaning, accepted values, units, absence/null/zero semantics, timestamp meaning or a generic connector contract.

### Minor repository release

A pre-1.0 minor may introduce new experimental capabilities and may carry an intentionally incompatible canonical or connector contract **only when the new contract has a distinct version and migration notes**.

A breaking canonical change must use a new canonical `schema_version` and a separate schema line. A breaking generic connector change must use a new `manifest_version`.

## Migration guarantees

For every published canonical schema version:

1. **Version identity is permanent.** An existing `schema_version` must not later acquire a different validation or business meaning.
2. **Historical schema lines remain available.** A new schema line is added alongside released historical lines rather than replacing them.
3. **Unknown versions fail closed.** Validators and consumers must require deliberate version support.
4. **Migration notes are required for contract changes.** They must state the old representation, new representation, whether conversion is lossless, and at least one deterministic example when conversion exists.
5. **Lossy conversion is never disguised as migration.** If a new contract requires information absent from an old record, the migration must report that the conversion is incomplete or unsupported rather than invent data.
6. **Provenance and identity are preserved when possible.** Migration must not replace source identifiers, currencies, timestamps, tax meaning or refund direction with guessed values.
7. **No automatic downgrade guarantee exists.** A newer record may contain semantics that cannot be represented in an older contract.
8. **No generic migration engine is promised yet.** Migration tooling is added only when a second real canonical schema version creates repeated, testable conversion work.

Schema directories may receive non-semantic documentation corrections, but released validation and field meaning for the same `schema_version` must remain stable.

## Closed-schema compatibility

Canonical objects currently use `additionalProperties: false`. Therefore adding an optional-looking canonical property can still cause an older strict validator to reject a newer record.

Such an addition is **not automatically backward-compatible**. Before 1.0 it belongs in a new schema line unless compatibility with the existing validator is actually preserved. After 1.0 it is a major-version change unless a future contract explicitly creates a backward-compatible extension mechanism.

Namespaced `extensions` are the current mechanism for carrying provider-specific information without turning every provider field into a universal canonical property.

## Deprecation

Deprecation is documentation, not permission to reinterpret records.

Before 1.0:

- a deprecated behavior may remain supported while a replacement is introduced;
- removal or semantic replacement still requires a new contract version and migration notes.

After 1.0:

- patch releases cannot remove supported canonical behavior;
- minor releases may deprecate behavior and add changes that are demonstrably backward-compatible;
- breaking removal or reinterpretation requires a new major contract version.

## 1.0 transition

This policy defines how a stable contract would evolve; it does **not** declare OpenRetailSchema ready for 1.0.

The roadmap keeps the actual 1.0 readiness gate separate. At minimum, stable-version planning remains blocked until real adoption evidence and at least one live-tested reference connector justify freezing long-term compatibility promises.

When a 1.0 candidate is eventually proposed, the release review must identify:

- the exact canonical schema chosen for 1.0;
- the connector-manifest version supported at 1.0;
- any migration from the latest pre-1.0 schema;
- the backward-compatibility test matrix;
- the support/deprecation window for historical schema lines.

## Release checklist for a contract change

A pull request that changes a canonical or generic connector contract must answer all of the following before merge:

- Which version axis changes?
- Is the change compatible with the existing validator/manifest harness?
- Which previously valid records or adapters would stop conforming?
- Is a new schema directory or manifest version required?
- Are migration notes and synthetic old/new examples present?
- Are unknown/absence semantics preserved?
- Do the complete repository tests pass on the exact proposed release state?

If those questions cannot be answered, the contract change is not ready to publish.
