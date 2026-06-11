# Changelog

## 0.1.0 - Draft

### Added

- Added the hardened Regis `TwinProjectionFeature.v0.1` contract as the canonical HolographMe → Regis projection-feature surface.
- Added positive fixtures for object, string, boolean, number, and array `feature_value` shapes.
- Added negative fixtures covering denied-field emission, unsafe free-text reason leakage, raw twin payload leakage, `DoNotLearn` violations, `DoNotLink` violations, unknown feature families, unsafe authority bands, bad hashes, revocation replay, expired consent, missed authority downgrade, and null feature values.
- Added `docs/regis/twin-projection-feature-v0.1.md` documenting ownership boundaries, Draft 2020-12 posture, non-null feature semantics, canonical JSON v0.1 hashing, `content_hash`, `lineage_hash`, safe reason vocabulary, authority lattice behavior, and fixture strategy.

### Changed

- Tightened `TwinProjectionFeature` from a permissive shape to a closed contract with sealed vocabularies and required governance controls.
- Updated Regis example validation to apply negative mutation fixtures and require each fixture to include its declared `expected_failure` in the computed failure-code set.
- Added semantic validation for `content_hash`, `lineage_hash`, lineage consistency, expiry handling, revocation posture, and authority greatest-lower-bound behavior.

### Governance controls covered

- `DoNotLearn`
- `DoNotLink`
- `NoRawTwinExport`
- denied/forbidden field exclusion
- null/absence suppression
- revocation propagation
- authority downgrade
- hash and lineage integrity

### Follow-on

- HolographMe should validate exporter output against this contract once this draft lands.
- Regis should add a graph-delta ingest fixture for this feature record.
- Policy Fabric should add the first `DoNotLearn` admission rule.
- AgentPlane / Operation Plane should carry this feature through an admitted operation with receipt evidence.
