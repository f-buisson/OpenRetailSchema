## Scope

Describe the interoperability problem and the smallest change that solves it.

- Provider / product / edition / API or export version:
- Canonical schema version affected:
- Official source links and date checked:

## Evidence level

Mark only what this change actually proves.

- [ ] Public documentation reviewed
- [ ] Synthetic fixtures exercised
- [ ] Authorized external account behavior observed
- [ ] OpenRetailSchema connector live-tested

Do not promote one evidence level into another. A public endpoint or green unit test is not live-provider certification.

## Mapping boundaries

Describe relevant edge cases and unsupported behavior, especially:

- missing / null / zero values
- money, currency and tax inclusion
- timestamp timezone or UTC-offset semantics
- refunds / returns and sign conventions
- pagination, checkpoints, retries and access limits
- provenance and any namespaced source extensions

## Provenance and licensing

State where every contributed code fragment, fixture and documentation claim came from. Contributions intended for inclusion must be original work or material that may legally be redistributed under Apache-2.0 with any required notices preserved.

Do not include private project source, restricted vendor documentation, real customer or employee data, credentials, or unredacted provider payloads.

## Verification

List the exact commands that were actually run and their result. Do not list unexecuted tests.

```text
# example
python -m unittest discover -s tests -v
```

The public `Tests` workflow is supplementary regression evidence. It does not replace authorized provider testing when a live claim is made.

## Remaining gaps

List external access requirements, unsupported capabilities, uncertain semantics, or follow-up work.