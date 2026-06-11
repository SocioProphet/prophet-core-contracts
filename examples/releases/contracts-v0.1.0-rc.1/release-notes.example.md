# contracts-v0.1.0-rc.1 Release Notes

Status: example release notes for the contract release and downstream pinning protocol.

## Included contracts

- TwinProjectionFeature v0.1.0
- PolicyRequest v0.1.0
- PolicyDecision v0.1.0
- AdmissionToken v0.1.0
- Effect v0.1.0 experimental
- AuditRecord v0.1.0 experimental

## Validation gate

This release candidate must be cut only after:

```bash
make validate
```

passes on the release commit.

## Downstream pinning

Downstream consumers should pin both:

- `release_tag`
- `release_commit`

and verify `manifest_sha256` against `releases/contracts-v0.1.0-rc.1/manifest.json`.

## Notes

This is an example file. The real release notes for an actual tag must describe the exact contracts, schemas, validators, and compatibility posture included in that release.
