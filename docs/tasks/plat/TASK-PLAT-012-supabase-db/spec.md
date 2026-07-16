---
id: TASK-PLAT-012
title: "Supabase Postgres wiring - apply db/migrations to Supabase (pooler + direct URLs), migrate.sh idempotent apply, RLS session vars documented, no schema drift from TASK-PLAT-003"
module: PLAT
priority: MUST
status: done
phase: P3
slice: 1
lang: iac/sql
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-13
refs: [cyberos deploy/vps/migrate.sh, TASK-PLAT-003, strategy RISK-5]
related_frs: [TASK-PLAT-003, TASK-PLAT-011, TASK-PLAT-013, TASK-API-004, TASK-AUTH-001]
depends_on: [TASK-PLAT-003, TASK-PLAT-011]
blocks: [TASK-PLAT-013]
new_paths:
  - deploy/vps/migrate.sh
  - docs/deploy/supabase.md
  - supabase/config.toml
  - supabase/README.md
---

## §1 - Description (BCP-14 normative)

This task wires the existing TASK-PLAT-003 migrations (`db/migrations/*.sql`) to a **Supabase** project as the production database. It SHALL provide:

1. Documented connection modes: **direct** (`db.<ref>.supabase.co:5432`) for migrations/admin; **pooler** (transaction/session) for the API runtime when appropriate.
2. An idempotent `deploy/vps/migrate.sh` that applies ordered SQL files once (tracked in a `_strategem_schema_migrations` table or equivalent).
3. Documentation of RLS session GUC names used by policies (`app.current_user_id`, `app.current_role` per TASK-PLAT-003) and how the API sets them per request.
4. Optional `supabase/config.toml` for local `supabase start` parity — production remains hosted Supabase.

The task does NOT redesign tables (TASK-PLAT-003 owns schema). It does NOT deploy the API (TASK-PLAT-013).

## §2 - Why this design

CyberOS applies per-service migrations on the VPS against Supabase before container roll. Strategem has one product schema under `db/migrations/`; the same “migrate then start API” order prevents the API from talking to an unmigrated DB. Pooler vs session notes prevent the classic RLS + PgBouncer footgun.

## §3 - Contract

```bash
# on VPS or CI with secrets
export DATABASE_URL='postgresql://...'   # prefer direct for migrate
bash deploy/vps/migrate.sh
```

Migrate script SHALL:

- require `DATABASE_URL`
- create migrations ledger table if missing
- apply each `db/migrations/NNNN_*.sql` not yet recorded, in name order
- exit non-zero on failure; never skip failed file

## §4 - Acceptance criteria

1. `migrate.sh` is executable and dry-run documented.
2. `docs/deploy/supabase.md` lists env vars and RLS session setup.
3. Existing `db/migrations/0001`–`0009` are the apply set (no duplicate schema).
4. A local test can run migrations against ephemeral Postgres (CI already has Postgres service).

## §5 - Verification

- Script shellcheck-clean enough for CI; unit: ledger inserts once (optional pytest with testcontainers/psql).
- Docs link topology TASK-PLAT-011.
