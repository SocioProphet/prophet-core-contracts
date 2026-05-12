# Contract Release and Downstream Pinning v0.1

Status: read-ahead protocol for issue #15.

This document defines how `SocioProphet/prophet-core-contracts` publishes coherent contract snapshots and how downstream repositories pin them.

## Release tags

Use repo-level release tags:

```text
contracts-v0.1.0
contracts-v0.1.1
contracts-v0.2.0
```

Release candidates may use:

```text
contracts-v0.1.0-rc.1
```

Release tags are immutable. If a release tag is wrong, publish a patch release or a new release candidate. Do not move the tag.

## First stable release

The first stable release should be `contracts-v0.1.0`.

It should be published only after the coherent v0.1 admission spine is merged and `make validate` is green on the release commit.

Consumers may test against `contracts-v0.1.0-rc.N`, but runtime implementation should pin production work to the final stable tag unless explicitly marked experimental.

## Versioning policy

Before `contracts-v1.0.0`, this repo uses pre-1.0 semver:

- Patch release: documentation fixes, examples, validator fixes that do not reject previously valid conformant fixtures, or non-breaking corrections.
- Minor release: new contracts, new optional fields, new validators, or validator tightening that can reject previously valid fixtures.
- Major release: reserved for production-frozen breaking changes after v1.0.

Adding a required schema field or removing an enum value is not a patch.

## Release manifest

Every release tag must include:

```text
releases/<tag>/manifest.json
```

The manifest validates against:

```text
schemas/release-manifest.schema.json
```

The manifest records:

- release tag;
- release commit;
- release status;
- contracts included;
- schema paths and hashes;
- validator paths and hashes;
- canonicalization profiles;
- changelog reference;
- compatibility statement;
- validation status.

## Downstream pinning

Downstream repos should pin contract releases in:

```text
contracts/pinned-prophet-core-contracts.json
```

The pin validates against:

```text
schemas/pinned-prophet-core-contracts.schema.json
```

A downstream pin must include both:

- `release_tag`
- `release_commit`

The tag is human-readable. The commit is the cryptographic source of truth. Downstream PRs should also record the release manifest hash.

## Implementation gate

Downstream runtime implementation must not target draft branches.

Allowed:

- read-ahead planning against draft PRs;
- worksheet comments referencing draft PRs;
- experimental local tests against release candidates.

Not allowed:

- production or runtime conformance implementation against untagged feature branches;
- downstream pins to open PR heads;
- moving release tags after downstream repos have pinned them.

## Upgrade protocol

Downstream upgrades happen by PR.

Each upgrade PR should:

1. update `contracts/pinned-prophet-core-contracts.json`;
2. update any vendored schema/validator files;
3. update conformance fixtures if the release changes behavior;
4. run the downstream conformance suite;
5. link to the upstream release manifest.

## Validation

Run:

```bash
make validate-release-manifest
```

or the full suite:

```bash
make validate
```

## Non-goals

- No schema hosting service implementation.
- No package registry publication.
- No downstream runtime implementation.
- No actual release tag is created by this document.
