# Supabase database (FR-PLAT-012)

## Schema source of truth

Forward-only SQL: `db/migrations/0001_*.sql` … `0009_*.sql` (FR-PLAT-003).

## Connection URLs

| Mode | Use |
|---|---|
| **Direct** `db.<project-ref>.supabase.co:5432` | `migrate.sh`, admin, long transactions |
| **Pooler** (Supabase pooler host) | API runtime when many short connections |

Set on the VPS:

```bash
DATABASE_URL=postgresql://postgres.<ref>:<password>@aws-0-...pooler.supabase.com:6543/postgres
# or direct for migrate:
DATABASE_URL_MIGRATE=postgresql://postgres:<password>@db.<ref>.supabase.co:5432/postgres
```

## Apply migrations

```bash
export DATABASE_URL="$DATABASE_URL_MIGRATE"   # prefer direct
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
# optional: supabase CLI
# supabase start
# or plain Postgres:
export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/strategem
bash deploy/vps/migrate.sh
```

## Secrets

Never commit project passwords. Store in VPS `.env` and CI secrets only.
