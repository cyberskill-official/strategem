---
artefact: code-review@1
fr_id: TASK-LASO-001
module: laso-envelope
class: improvement
status: ready_for_human_acceptance
reviewer: ship-tasks (agent)
reviewed_at: 2026-07-13
impl_commit: 0137fc20a2d8ee1c460c24885c3877418b56aba0
verdict_pending: human reviewing → ready_to_test
---

# Code review — TASK-LASO-001 (supported envelope versions SoT)

## Scope of diff

Commit `0137fc2` (`feat: add task`) — pure refactor + coverage:

| Path | Change |
|---|---|
| `packages/laso_envelope/src/laso_envelope/models.py` | Extract `SUPPORTED_ENVELOPE_VERSIONS: frozenset[int] = frozenset({1})`; `require_supported_version` membership-checks that constant |
| `packages/laso_envelope/src/laso_envelope/__init__.py` | Re-export `SUPPORTED_ENVELOPE_VERSIONS` from package root + `__all__` |
| `packages/laso_envelope/tests/test_contract.py` | Import constant; add `test_supported_versions_single_source_of_truth` |

No schema, wire-format, or Rust-parity change.

## §1 clause → test map

| §1 clause | Evidence | Named test | Result |
|---|---|---|---|
| 1. SoT constant `SUPPORTED_ENVELOPE_VERSIONS: frozenset[int]` in `laso_envelope.models`, re-exported from package root | `models.py:75`, `__init__.py:8,21` | `test_supported_versions_single_source_of_truth` (import from `laso_envelope`) | **pass** |
| 2. `require_supported_version` decides solely by membership; `ValueError` lists supported versions | `models.py:80-86` | `test_supported_versions_single_source_of_truth` (`match=r"supported"`) + `test_rejects_unsupported_version` | **pass** |
| 3. Behaviour unchanged for `{1}`: v1 accepted; other int raises | same | golden path tests call `require_supported_version` on v1 fixtures; bad version raises | **pass** |
| 4. Tests assert (a) `1 in SUPPORTED…` (b) v1 accepted (c) unsupported raises with supported set in message | `test_contract.py:109-117` | `test_supported_versions_single_source_of_truth` | **pass** |

## Gate evidence (machine)

```
uv run pytest -q packages/laso_envelope --cov=laso_envelope --cov-report=term-missing
........                                                                 [100%]
packages/laso_envelope/src/laso_envelope/__init__.py   100%
packages/laso_envelope/src/laso_envelope/models.py      100%
TOTAL                                                  100%
```

Touched-file coverage ≥ 90%: **yes** (100%).

## Review checklist

| Check | Result |
|---|---|
| Correctness vs task | PASS — matches all 4 normative clauses |
| Behaviour parity | PASS — still accepts v1, rejects others with named supported set |
| Readability | PASS — single named constant, no magic inline set |
| Secrets / injection | N/A (no IO, no user input beyond already-validated model) |
| Backwards compatibility | PASS — public API additive (`SUPPORTED_ENVELOPE_VERSIONS` export only) |
| Oversized diff | PASS — ~25 lines |

## Findings

None blocking. No SECURITY-class items.

## Recommendation

**Approve** review acceptance: flip `reviewing → ready_to_test` so the testing phase (coverage-gate formal artefact, TRACE-004 closure, awh/caf if present) can run. Agent will not set `done`.

## Human gate (required)

Record one of:

- `APPROVE review TASK-LASO-001` — advances to `ready_to_test`
- `REJECT review TASK-LASO-001: <reason>` — routes back to `ready_to_implement`
