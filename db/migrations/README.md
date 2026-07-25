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
| `0010_app_query_store.sql` | Full cast JSON payload store (GET-by-id) |
| `0011_anon_user.sql` | Well-known anonymous user for public cast → domain tables |

## Apply path (human / CI)

Against an empty database (Postgres 16+ recommended):

```bash
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/strategem

# One-shot apply (preferred helper) — ledgered / idempotent
just db-migrate

# Or raw psql
for f in db/migrations/*.sql; do
  psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -f "$f"
done
```

Python helper (lexicographic order, ledgered via `_strategem_schema_migrations`):

```bash
uv run python -m db_schema.migrate
```

Local compose runs this automatically via the `migrate` service before the API starts.

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
