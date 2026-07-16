---
artefact: coverage-gate@1
fr_id: TASK-LASO-001
outcome: PASS
tests_failed: 0
---

# Coverage gate — TASK-LASO-001

## Command

```
uv run pytest -q packages/laso_envelope --cov=laso_envelope --cov-report=term-missing
```

## Result

```
........                                                                 [100%]
packages/laso_envelope/src/laso_envelope/__init__.py   100%
packages/laso_envelope/src/laso_envelope/models.py      100%
TOTAL                                                  100%
```

## TRACE-004 (§1 clause → test)

| Clause | Test | Status |
|---|---|---|
| 1 SoT constant + re-export | `test_supported_versions_single_source_of_truth` | passed |
| 2 membership-only + message lists supported | same + `test_rejects_unsupported_version` | passed |
| 3 v1 accepted / other raises | golden fixtures + SoT test | passed |
| 4 explicit asserts (a)(b)(c) | `test_supported_versions_single_source_of_truth` | passed |

## Module gates

- awh: N/A (no `modules/laso-envelope/.awh/`)
- caf: N/A (`CAF_ENABLED=false`)

## files_below_90pct

(empty)
