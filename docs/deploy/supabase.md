# Supabase database (TASK-PLAT-012 + D-DB-001)

## Schema source of truth

Forward-only SQL: `db/migrations/*.sql` (TASK-PLAT-003). Runtime LOGIN role: `0017_runtime_app_role.sql`.

## Connection URLs

| Mode | Use |
|---|---|
| **Direct** `db.<project-ref>.supabase.co:5432` as privileged role | `migrate.sh`, admin, long transactions (`DATABASE_URL_MIGRATE`) |
| **Pooler** as `strategem_app` | API runtime (`DATABASE_URL`) — **must** be `NOSUPERUSER NOBYPASSRLS` |

### HITL — apply restricted role on hosted Supabase

1. Connect as the project privileged role (dashboard SQL or `psql` on the **direct** URL).
2. Apply migrations (creates `strategem_app` with local default password):
   ```bash
   export DATABASE_URL_MIGRATE='postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres'
   export DATABASE_URL="$DATABASE_URL_MIGRATE"
   bash deploy/vps/migrate.sh
   ```
3. **Rotate** the runtime password (required before any shared environment):
   ```sql
   ALTER ROLE strategem_app PASSWORD '<strong-random>';
   ```
4. Grant pooler access if your project uses a pooler username form; ensure the login can `CONNECT` to the database.
5. Set VPS / platform secrets:
   ```bash
   DATABASE_URL=postgresql://strategem_app:<strong>@<pooler-host>:6543/postgres
   DATABASE_URL_MIGRATE=postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres
   ```
6. Restart API. Startup must succeed without `ALLOW_PRIVILEGED_DB`. If it raises `NOSUPERUSER NOBYPASSRLS`, the URL is still privileged — fix the role, do not set the break-glass flag in production.

### HITL — local Docker compose

```bash
# migrate service uses postgres; api service uses strategem_app (see docker-compose.local.yml)
just local-up
# or:
docker compose -f deploy/compose/docker-compose.local.yml up --build -d
```

Default local password for `strategem_app` is `strategem_app` (override with `STRATEGEM_APP_PASSWORD` **and** `ALTER ROLE` if you change it after first migrate).

Set on the VPS:

```bash
DATABASE_URL=postgresql://strategem_app:PASSWORD@aws-0-...pooler.supabase.com:6543/postgres
DATABASE_URL_MIGRATE=postgresql://postgres:PASSWORD@db.xxxx.supabase.co:5432/postgres
```

## Apply migrations

```bash
export DATABASE_URL="$DATABASE_URL_MIGRATE"   # prefer direct + privileged
bash deploy/vps/migrate.sh
```

The script records applied files in `_strategem_schema_migrations`.

## RLS session variables

Policies expect (see `db/migrations/0009_rls_policies.sql` / `db/rls/session.md`):

- `app.current_user_id` — UUID of the authenticated subject
- `app.current_role` — optional admin bypass role name

The API MUST `SET LOCAL` these per transaction after JWT validation. A connection without them sees **zero** user rows (fail-closed).

## Local parity

```bash
export DATABASE_URL_MIGRATE=postgresql://postgres:postgres@localhost:5432/strategem
export DATABASE_URL="$DATABASE_URL_MIGRATE"
bash deploy/vps/migrate.sh
# then run API as:
export DATABASE_URL=postgresql://strategem_app:strategem_app@localhost:5432/strategem
```

## Secrets

Never commit project passwords. Store in VPS `.env` and CI secrets only. Never set `ALLOW_PRIVILEGED_DB=1` in staging/production.
