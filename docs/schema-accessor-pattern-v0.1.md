# Schema Accessor Pattern v0.1

Status: read-ahead convention for admission-chain validators and future cross-contract validators.

## Purpose

Cross-contract validators must not hardcode JSON paths throughout invariant functions.

Each contract schema should have a small accessor class or accessor module that is the single source of truth for reading contract fields. Invariant code should call accessors, not raw nested paths.

This prevents read-ahead and validator code from drifting when a schema uses nested fields, renamed fields, or version-specific layouts.

## Rule

For every contract used in cross-contract validation, define a schema-aware accessor:

- `PolicyRequestAccessor`
- `PolicyDecisionAccessor`
- `AdmissionTokenAccessor`
- `EffectAccessor`
- `AuditRecordAccessor`

Invariant functions must use these accessors.

Do not write invariants like:

```python
bundle.policy_request["requesting_actor_id"]
```

when the actual schema uses:

```python
bundle.policy_request["requesting_actor"]["actor_id"]
```

Instead, write:

```python
request = PolicyRequestAccessor(bundle.policy_request)
request.requesting_actor_id
```

## Accessor responsibilities

An accessor may:

1. expose stable semantic properties;
2. hide schema nesting and version-specific layout;
3. raise clear `KeyError` / `ValueError` messages for malformed documents;
4. convert lists into lookup maps where appropriate;
5. centralize version-specific migration shims when v0.2 appears.

An accessor must not:

1. silently repair invalid documents;
2. perform policy decisions;
3. mutate the source document;
4. bypass per-contract schema validation.

## Example pattern

```python
from collections.abc import Mapping
from typing import Any

class PolicyRequestAccessor:
    def __init__(self, doc: Mapping[str, Any]) -> None:
        self._doc = doc

    @property
    def schema_version(self) -> str:
        return self._doc["schema_version"]

    @property
    def request_id(self) -> str:
        return self._doc["request_id"]

    @property
    def request_hash(self) -> str:
        return self._doc["request_hash"]

    @property
    def requesting_actor_id(self) -> str:
        return self._doc["requesting_actor"]["actor_id"]

    @property
    def subject_actor_id(self) -> str:
        return self._doc["subject_actor"]["actor_id"]
```

```python
class PolicyDecisionAccessor:
    def __init__(self, doc: Mapping[str, Any]) -> None:
        self._doc = doc

    @property
    def decision_id(self) -> str:
        return self._doc["decision_id"]

    @property
    def request_id(self) -> str:
        return self._doc["policy_request_ref"]["request_id"]

    @property
    def input_hash(self) -> str:
        return self._doc["input_hash"]

    @property
    def risk_tier(self) -> str:
        return self._doc["risk_tier"]

    @property
    def restrictions(self) -> set[str]:
        return set(self._doc.get("restrictions", []))

    def granted_action(self, action_id: str) -> Mapping[str, Any]:
        for action in self._doc.get("granted_actions", []):
            if action.get("action_id") == action_id:
                return action
        raise KeyError(f"granted action not found: {action_id}")
```

## Cross-contract invariant example

```python
def check_admission_token_request_id(bundle: FixtureBundle) -> InvariantResult:
    inv_id = "admission_token_request_id_mismatch"
    if bundle.admission_token is None or bundle.policy_request is None:
        return _na(inv_id, 4)

    request = PolicyRequestAccessor(bundle.policy_request)
    token = AdmissionTokenAccessor(bundle.admission_token)

    if token.policy_request_id != request.request_id:
        return InvariantResult(
            inv_id,
            4,
            passed=False,
            detail=(
                f"token.policy_request_id={token.policy_request_id}, "
                f"request.request_id={request.request_id}"
            ),
        )
    return InvariantResult(inv_id, 4, passed=True)
```

## Validation sequence

The recommended sequence is:

1. run per-contract schema validation;
2. wrap valid documents with accessors;
3. run cross-contract invariants through accessors;
4. emit stable failure codes.

Accessors are not a replacement for schema validation. They are the bridge between schema-shaped documents and semantic invariant code.

## Versioning

Accessor classes are version-bound. v0.1 accessors read v0.1 schemas.

When v0.2 schemas introduce layout changes, either:

1. add v0.2 accessor classes alongside v0.1; or
2. add explicit version dispatch inside a thin accessor factory.

Do not make v0.1 accessors silently accept v0.2 shapes.

## Admission-chain application

PR #11 should use accessors for invariants #1-#13.

PR #12 should extend the pattern for AuditRecord invariants.

Prior read-ahead code snippets that hardcoded concrete JSON paths should be treated as sketches unless they match the actual current schema and accessor conventions.
