---
artefact: coverage-gate@1
fr_id: TASK-PLAT-003
outcome: PASS
tests_failed: 0
---

# Coverage gate — TASK-PLAT-003

## Command

```
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/strategem \
  uv run pytest -q packages/db_schema --cov=db_schema --cov-report=term-missing
```

## Result

```
..................                                                       [100%]
packages/db_schema/src/db_schema/__init__.py  100%
packages/db_schema/src/db_schema/migrate.py    97%  (only `if __name__` guard)
TOTAL                                          98%
18 passed
```

## TRACE-004 (§4 AC → test)

| AC | Test | Status |
|---|---|---|
| 1 tables + GIN + RLS forced | `test_schema_objects_exist`, unit inventory | passed |
| 2 fail-closed unset GUC | `test_fail_closed_unset_guc` | passed |
| 3 isolation A vs B | `test_isolation_user_a_cannot_see_b` | passed |
| 4 admin explicit | `test_admin_bypass_explicit` | passed |
| 5 GIN containment | `test_gin_index_used_for_containment` | passed |
| 6 forward-only docs | `db/migrations/README.md` | present |
| 7 bytea + deleted_at | `test_schema_objects_exist` | passed |

## Module gates

- awh: N/A (no sealed goldenset for PLAT/db)
- caf: N/A (`CAF_ENABLED=false`)

## files_below_90pct

(empty)
