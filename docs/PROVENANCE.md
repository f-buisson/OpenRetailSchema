# Repository provenance and licence review

[Contributing](../CONTRIBUTING.md) · [External references](EXTERNAL_REFERENCES.md) · [Roadmap](ROADMAP.md)

This document records the repository's provenance baseline and the review required before third-party material is incorporated. It is an engineering provenance record, not legal advice.

## Baseline — 2026-10-07

Baseline commit: `3e4fac1857f07524418b570e85fab36ac3a56449`.

The review covered the complete Git commit history available at this baseline, all repository pull requests, the full tracked tree, declared Python dependencies, the public test workflow and searches for third-party source/licence markers.

### Authorship and accepted contributions

- Git history contains **237 commits**. Every commit records `f-buisson` as the Git author. GitHub may appear as the committer on merge/squash commits; that is repository hosting metadata, not separate source authorship.
- The repository contains **36 historical pull requests** at this baseline. All 36 were opened by `f-buisson`.
- Therefore no external contribution has been accepted into the repository at this baseline. This statement describes the observable repository history; it does not assert ownership of material outside the repository.

When an external contribution is first accepted, this section must be updated rather than relying on the original baseline.

### Tracked-source review

The baseline tree contains **88 tracked entries**. A path review found no vendored dependency tree, third-party source directory, generated SDK bundle, copied distribution tree or third-party notice file. Repository code search found no third-party copyright header outside the project's own Apache-2.0 licence text.

Names of external projects such as Loyverse SDKs, Square SDKs and Airbyte connectors occur in [EXTERNAL_REFERENCES.md](EXTERNAL_REFERENCES.md) as research references with explicit use restrictions. They are not evidence that those sources or fixtures were copied into this repository.

### Declared dependencies and tooling

| Component | Use in this repository | Upstream licence observed | Incorporation status |
| --- | --- | --- | --- |
| `jsonschema>=4.20,<5` | Python schema validation and tests | MIT | Installed dependency; source is not vendored |
| `actions/checkout@v4` | Public CI checkout step | MIT | Workflow dependency; source is not vendored |
| `actions/setup-python@v5` | Public CI Python setup | MIT | Workflow dependency; source is not vendored |

Upstream licence references checked on 2026-10-07:

- [python-jsonschema/jsonschema — COPYING](https://github.com/python-jsonschema/jsonschema/blob/main/COPYING)
- [actions/checkout — LICENSE](https://github.com/actions/checkout/blob/main/LICENSE)
- [actions/setup-python — LICENSE](https://github.com/actions/setup-python/blob/main/LICENSE)

Transitive packages installed by package tooling are not copied into this repository. Their own licence obligations remain attached to those packages. If the project later distributes bundled dependencies, a separate distribution-level notice/licence review is required.

## Apache-2.0 repository boundary

OpenRetailSchema is licensed under [Apache License 2.0](../LICENSE). The repository licence does not automatically relicense third-party material.

Before copying or adapting any third-party code, fixture, schema fragment, documentation text or generated source into the repository, the change must record:

1. the upstream project and exact file/source;
2. the upstream version, tag or commit when applicable;
3. the upstream licence and whether redistribution/modification is permitted for the proposed use;
4. any copyright, attribution or NOTICE text that must be preserved;
5. which repository files contain the incorporated material;
6. why original implementation from public specifications is insufficient.

If compatibility or redistribution rights are unclear, do not incorporate the material. Refer to it for research and independently implement behavior from public specifications instead.

## Provider data and private-source boundary

Provider documentation, account access and observed behavior are evidence, not source-code provenance.

Do not incorporate:

- private F-Buisson project source into this Apache-2.0 repository unless provenance and compatible rights are explicitly established;
- restricted vendor SDK or documentation text;
- real provider payloads, customer/employee data, credentials or unredacted exports;
- public test fixtures whose provenance, privacy status or redistribution rights are unclear.

Use wholly synthetic fixtures written for OpenRetailSchema whenever provider behavior can be represented without copying source data.

## Pull-request review gate

For every future external contribution or any change that incorporates third-party material:

- require the provenance/licensing section of the pull-request template;
- compare the proposed licence with Apache-2.0 distribution requirements;
- preserve required notices before merge;
- keep vendor evidence level separate from source provenance;
- reject secrets, private data and restricted material;
- run the repository regression suite, while treating CI as code-regression evidence rather than provider certification.

A new dependency does not require copying its source into this repository. Prefer normal package dependencies with their upstream licence intact when that is sufficient.

## Re-audit triggers

Repeat or extend this audit when any of the following occurs:

- the first pull request from an external contributor is accepted;
- third-party source or generated vendor code is proposed;
- a dependency is bundled into a release artifact rather than installed separately;
- a new licence, NOTICE file or dual-licensing model is introduced;
- release packaging changes what third-party material is distributed.

Until one of these triggers occurs, this baseline remains the provenance reference for the current repository contents.
