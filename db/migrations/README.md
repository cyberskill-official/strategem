# Database migrations (TASK-PLAT-003)

Forward-only SQL migrations for the Tam Thuc Strategem data tier. No ORM owns this schema; both the Rust engine branch and the Python API/RAG branch target the same DDL.

## Files (apply in order)

| File | Purpose |
|---|---|
| `0001_init_extensions.sql` | `pgcrypto`, `citext` (+ reserved `pgvector` note) |
| `0002_users.sql` | Users + soft-delete + opaque `birth_data_encrypted` |
| `0003_queries.sql` | Cast requests |
| `0004_charts.sql` | La so envelopes (`jsonb`) |
| `0005_knowledge_patterns.sql` | Pattern table (conditions `jsonb`) |
| `0006_reports.sql` | Interpretation + AI disclosure |
| `0007_audit_logs.sql` | Sensitive-access audit trail |
| `0008_indexes_gin.sql` | GIN on JSONB + btree helpers |
| `0009_rls_policies.sql` | Fail-closed RLS + `app_user` / `app_admin` roles |
| `0010_app_query_store.sql` | Product query/chart/report payload store |
| `0012_app_query_store_rls.sql` | RLS on `app_query_store` (TT-008); after `0011_anon_user` on main |
| `0013_auth_users_columns.sql` | AUTH columns on `users` (TT-024) |
| `0014_refresh_token_revocations.sql` | Durable refresh jti denylist (TT-024) |
| `0015_payment_fulfillments.sql` | PayOS webhook idempotency |
| `0016_operator_llm_settings.sql` | Operator BYOK LLM settings |
| `0017_runtime_app_role.sql` | `strategem_app` LOGIN (`NOSUPERUSER NOBYPASSRLS NOCREATEDB`) for API runtime (D-DB-001) |

## Apply path (human / CI)

Against an empty database (Postgres 16+ recommended):

```bash
# Privileged role for migrate only
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/strategem

# One-shot apply (preferred helper)
just db-migrate

# Or raw psql
for f in db/migrations/*.sql; do
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
done
```

Python helper (same order, used by tests):

```bash
uv run python -m db_schema.migrate
```

Migrations use a ledger table `public._strategem_schema_migrations` (same as
`deploy/vps/migrate.sh`). Re-running `db_schema.migrate` skips already-applied
files; each new file is applied in its own transaction.

After migrate, point the **API** at the restricted role (not `postgres`):

```bash
export DATABASE_URL=postgresql://strategem_app:strategem_app@localhost:5432/strategem
# optional: keep migrate URL separate
export DATABASE_URL_MIGRATE=postgresql://postgres:postgres@localhost:5432/strategem
```

Startup refuses superuser / `BYPASSRLS` connections unless `ALLOW_PRIVILEGED_DB=1`
(break-glass only). See [`../rls/session.md`](../rls/session.md).

## RLS session contract

See [`../rls/session.md`](../rls/session.md). Every app connection that reads user-scoped data **must** `SET LOCAL app.current_user_id` (and `app.current_role` for admin) inside the transaction. An unset GUC returns **zero rows**, never all rows.

## Tests

```bash
# Requires a live Postgres (CI uses a service container)
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/strategem
just db-test
# or:
uv run pytest -q packages/db_schema
```

Isolation script (psql harness equivalent): `db/tests/test_rls_isolation.sql` — also executed via the Python suite.
