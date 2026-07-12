---
artefact: code-review@1
fr_id: FR-PLAT-003
status: ready_for_human_acceptance
reviewed_at: 2026-07-13
verdict_pending: human reviewing → ready_to_test
---

# Code review — FR-PLAT-003 (DB schema + migrations + RLS)

## Delivered paths

| Path | Role |
|---|---|
| `db/migrations/0001`…`0009_*.sql` | Extensions, six tables, GIN, RLS |
| `db/migrations/README.md` | Apply path |
| `db/rls/session.md` | SET LOCAL contract for AUTH/API |
| `db/tests/test_rls_isolation.sql` | SQL harness stub |
| `packages/db_schema/` | migrate helper + pytest isolation suite |
| `.github/workflows/ci.yml` | Postgres 16 service + `DATABASE_URL` |
| `justfile` | `db-migrate` / `db-test` / `db-gate` |

## §4 acceptance → tests

| AC | Test / evidence |
|---|---|
| 1. 0001..0009 produce tables, GIN, RLS forced | `test_schema_objects_exist`, `test_nine_ordered_migration_files` |
| 2. Fail-closed unset GUC | `test_fail_closed_unset_guc` |
| 3. Isolation A vs B | `test_isolation_user_a_cannot_see_b` |
| 4. Admin explicit bypass | `test_admin_bypass_explicit` |
| 5. GIN for containment | `test_gin_index_used_for_containment` (+ index inventory) |
| 6. Forward-only apply path documented | `db/migrations/README.md` |
| 7. `bytea` birth + `deleted_at` | `test_schema_objects_exist`, unit SQL scrape |

## Local gate evidence

```
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:5433/strategem
uv run pytest -q packages/db_schema   → 11 passed
uv run pytest -q                      → 20 passed (full python lane)
ruff + mypy packages/                 → clean
```

## Findings

None blocking. Notes:

- Superuser bypasses RLS; tests use non-superuser `strategem_app` / `strategem_admin` LOGIN roles created at test time.
- Tiny tables prefer seq scan; GIN EXPLAIN uses `enable_seqscan=off` to prove index usability (index also asserted in `pg_indexes`).

## Recommendation

**Approve** review acceptance (`reviewing → ready_to_test`).

Human: `APPROVE review FR-PLAT-003` or `REJECT review FR-PLAT-003: <reason>`.
