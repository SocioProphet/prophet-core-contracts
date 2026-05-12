# TwinProjectionFeature v0.1

`TwinProjectionFeature` is the canonical contract for consent-scoped HolographMe projection features consumed by the Regis Semantic Feature Plane.

It is a governed feature record. It is not raw twin state, not a canonical identity truth assertion, and not an authorization to learn, link, merge, or promote identity state.

## Ownership

- Canonical schema owner: `SocioProphet/prophet-core-contracts`
- Emitter: `SocioProphet/HolographMe`
- Consumer: `SocioProphet/regis-entity-graph`
- Policy admission: `SocioProphet/policy-fabric`
- Runtime receipt: `SocioProphet/agentplane` / Operation Plane

## Draft and version

The schema declares JSON Schema Draft 2020-12.

Consumers must reject unknown major versions. v0.1 minor/patch revisions are additive only when the canonical schema marks them additive.

## Feature value contract

`feature_value` accepts non-null JSON values only:

- string
- number
- boolean
- object
- array

`null` is intentionally excluded because null feature records can leak absence. Exporters should suppress null, missing, denied, or forbidden fields instead of emitting null features.

## Canonical JSON v0.1

`hash_canonicalization` is fixed to:

`canonical_json_v0.1_utf8_nfc_sorted_keys_no_insignificant_ws`

For v0.1 this means:

1. UTF-8 encoding.
2. Unicode strings are expected to be normalized to NFC by emitters before hashing.
3. Object keys are sorted lexicographically by Unicode code point.
4. No insignificant whitespace is emitted.
5. Arrays preserve order.
6. Booleans are serialized as `true` or `false`.
7. Numbers must be emitted in a stable JSON representation by the emitting runtime. Cross-language emitters should use RFC 8785 / JSON Canonicalization Scheme compatible number formatting where available.
8. `null` feature values are not allowed.

The current Python validator uses:

```python
json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

This is the repo-local v0.1 validator rule. If a later multi-language emitter requires stricter canonicalization, upgrade this contract to an RFC 8785-aligned minor version and update all fixtures.

## Hash fields

`content_hash` is:

```text
sha256(canonical_json(feature_value))
```

with the `sha256:` prefix.

Example string feature value:

```json
"remote_first"
```

canonical JSON:

```json
"remote_first"
```

content hash:

```text
sha256:6ce6d1da895e01a578136ea68479c3c5e49aaa62c9075e55f88f77205acef3a9
```

Example boolean feature value:

```json
true
```

canonical JSON:

```json
true
```

content hash:

```text
sha256:b5bea41b6c623f7c09f1bf24dcae58ebab3c0cdd90ad966bc43a45b44867e12b
```

`lineage_hash` is:

```text
sha256(projection_id || decision_log_id || policy_id || schema_version || created_at)
```

where `||` is the literal delimiter between UTF-8 string fields.

For the main fixture:

```text
proj_mission_fit_001||pdl_projection_001||cp_example_001||0.1.0||2026-05-04T18:31:00Z
```

lineage hash:

```text
sha256:27230052d7f1f34714d4c06f4d1ff2dff4544a23dd93331f9c001539cd4f44b4
```

`lineage_hash` intentionally hashes stable references and version/time pins, not the full contents of the projection, decision log, or policy. Deep contents remain available through their own evidence artifacts and hashes.

## Safe reason vocabulary

`source_field_reason` is a closed safe vocabulary. Free-text reason strings are forbidden because they can leak denied content or sensitive absence.

Allowed v0.1 values:

- `allowed_by_consent_policy`
- `allowed_by_projection`
- `allowed_by_policy_fabric`
- `purpose_bound_release`
- `field_minimized`
- `authority_sufficient`
- `subject_authorized`
- `policy_exception_admitted`

Sensitive explanation details must be referenced by a separately admitted evidence pointer, not embedded in `source_field_reason`.

## Authority lattice

Authority bands are ordered:

```text
observe < recommend < represent < negotiate < commit
```

`effective_authority_band` must be the greatest lower bound over available upstream authority bands:

- consent delegation maximum authority
- mission governance authority
- transition receipt approval band
- future delegated-agent authority, when carried in this contract
- future downstream policy gate authority, when carried in this contract

Absent authority sources do not increase authority. The safe default for a missing optional source is `observe` at the validator and admission layers.

JSON Schema enforces the closed enumeration. The semantic validator enforces the greatest-lower-bound rule.

## Hard controls

The v0.1 contract encodes these controls:

- `DoNotLearn`: `do_not_learn` must be `true`.
- `DoNotLink`: `do_not_link` must be `true`.
- `NoRawTwinExport`: `raw_twin_payload_present` must be `false` and additional raw payload fields are forbidden.
- Denied/forbidden field exclusion: `source_field_decision` must be `allow`.
- Revocation propagation: revoked or expired features cannot remain `allowed`.
- Authority downgrade: effective authority must be no greater than upstream authority.
- Hash integrity: `content_hash` and `lineage_hash` must match canonical inputs.

## Positive fixtures

The v0.1 fixture set covers these `feature_value` shapes:

- object: `examples/regis/twin-projection-feature.example.json`
- string: `examples/regis/twin-projection-feature.string.example.json`
- boolean: `examples/regis/twin-projection-feature.boolean.example.json`

## Negative fixtures

Negative fixtures live in `examples/regis/negative/`.

Each fixture mutates the positive object fixture and declares an `expected_failure`. The validator must observe that specific failure code in the computed failure-code set. This prevents tests from passing merely because validation failed somewhere unrelated.

Current failure classes include:

- denied field emitted
- unsafe reason leakage
- raw twin payload leakage
- missing `DoNotLearn`
- `DoNotLearn = false`
- `DoNotLink = false`
- unknown feature family
- unsafe authority band
- bad content hash
- bad lineage hash
- replay after revocation while still allowed
- expired consent while still active/allowed
- missed authority downgrade

## Validation

Run:

```bash
make validate
```

The Regis validation target runs `tools/validate_regis_examples.py`.
