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

Stable schema id:

```text
https://schemas.socioprophet.org/regis/twin-projection-feature/v0.1.schema.json
```

Consumers must reject unknown major versions. v0.1 minor/patch revisions are additive only when the canonical schema marks them additive.

## Feature value contract

`feature_value` accepts non-null JSON values only:

- string
- number
- boolean
- object
- array

`null` is intentionally excluded because null feature records can leak absence. Exporters should suppress null, missing, denied, or forbidden fields instead of emitting null features. The v0.1 validator includes a null-negative fixture to prevent accidental reintroduction.

## Canonical JSON v0.1

`hash_canonicalization` is fixed to:

```text
canonical_json_v0.1_utf8_nfc_sorted_keys_no_insignificant_ws
```

This is a custom v0.1 canonicalization rule, not a full RFC 8785 claim. It is intentionally close to JSON Canonicalization Scheme practice, but the reference validator defines the active v0.1 behavior. A future RFC 8785-aligned minor release may replace this rule after multi-language emitter tests exist.

For v0.1 this means:

1. UTF-8 encoding.
2. Unicode strings are expected to be normalized to NFC by emitters before hashing.
3. Object keys are sorted lexicographically by Unicode code point.
4. No insignificant whitespace is emitted.
5. Object member separators are `,` and key/value separators are `:` with no spaces.
6. Arrays preserve order and use `,` separators with no spaces.
7. Strings use JSON string escaping as emitted by the reference validator. Control characters, quotes, and backslashes are escaped; non-ASCII Unicode is emitted as UTF-8, not forced to `\uXXXX` escapes.
8. Booleans are serialized as `true` or `false`.
9. Numbers are serialized by the reference validator's JSON emitter. `NaN`, `Infinity`, and `-Infinity` are not valid JSON and must not be emitted. v0.1 does not claim cross-language numeric equivalence normalization: `1` and `1.0` are distinct canonical JSON strings and therefore distinct hashes. Emitters must not rewrite numeric representation after computing hashes.
10. `null` feature values are not allowed.

The current Python validator uses:

```python
json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
```

## Hash fields

Hashes use SHA-256 and are encoded as lowercase hexadecimal with the `sha256:` prefix. The hex digest is exactly 64 lowercase hexadecimal characters, with no separators and no `0x` prefix.

`content_hash` is:

```text
sha256(canonical_json(feature_value))
```

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

Example string with escapable characters:

```json
"line\nquote\"slash\\snowman☃"
```

canonical JSON:

```json
"line\nquote\"slash\\snowman☃"
```

content hash:

```text
sha256:51cd07f5aa5e6c882a33d546de8d96bbda0f6584759240894f8ad5fc2c78442a
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

Example number feature value:

```json
0.85
```

canonical JSON:

```json
0.85
```

content hash:

```text
sha256:1e181f0934d441445f03ff51c972ef44275b830c10a80401e53b27bf5baf327a
```

Number representation edge cases:

```text
1    -> canonical JSON 1    -> sha256:6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b
1.0  -> canonical JSON 1.0  -> sha256:d0ff5974b6aa52cf562bea5921840c032a860a91a3512f7fe8f768f6bbe005f6
-0.0 -> canonical JSON -0.0 -> sha256:c26617c7ccbcaa6631b45d851b8cf56e21d2ca624bdb1193afdbd4b560702cec
```

These are deliberately distinct in v0.1 because the custom rule follows the reference validator's JSON output rather than a numeric-normalization standard.

Example array feature value:

```json
["remote_first", "async_ok"]
```

canonical JSON:

```json
["remote_first","async_ok"]
```

content hash:

```text
sha256:0f6f68708dea87ebe8c8eb4cfe4f893cecdbfa3ec60f0f8ecaecaa9450b07fc0
```

Example mixed array feature value:

```json
["remote_first", true, 1, {"b": 2, "a": "x"}]
```

canonical JSON:

```json
["remote_first",true,1,{"a":"x","b":2}]
```

content hash:

```text
sha256:9251425141a6a2c40f9d328cf0cbfeb7e3d350b065a82d81e4c93a434fc97a35
```

Example nested object feature value:

```json
{"z": ["b", true, 2], "a": {"k": "v", "n": 1}}
```

canonical JSON:

```json
{"a":{"k":"v","n":1},"z":["b",true,2]}
```

content hash:

```text
sha256:26e849de2476aa63d4cb5455b7905a19d8119e1c012704dfabe23ff3b9a6b83f
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
- Null/absence suppression: `feature_value` must not be `null`.
- Revocation propagation: revoked or expired features cannot remain `allowed`.
- Authority downgrade: effective authority must be no greater than upstream authority.
- Hash integrity: `content_hash` and `lineage_hash` must match canonical inputs.

## Positive fixtures

The v0.1 fixture set covers these `feature_value` shapes:

- object: `examples/regis/twin-projection-feature.example.json`
- string: `examples/regis/twin-projection-feature.string.example.json`
- boolean: `examples/regis/twin-projection-feature.boolean.example.json`
- number: `examples/regis/twin-projection-feature.number.example.json`
- array: `examples/regis/twin-projection-feature.array.example.json`

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
- null feature value emitted

## Validation

Run:

```bash
make validate
```

The Regis validation target runs `tools/validate_regis_examples.py`.
