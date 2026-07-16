---
id: TASK-PLAT-003
title: "Postgres schema + migrations for the six data-tier tables (users, queries, charts, knowledge_patterns, reports, audit_logs), GIN indexes on the JSONB columns, and fail-closed row-level security for tenant/user isolation"
module: PLAT
priority: MUST
status: done
phase: P0
slice: 1
lang: iac
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-46, strategy 4.1, strategy 4.4, strategy RISK-5]
related_frs: [TASK-PLAT-001, TASK-PLAT-006, TASK-AUTH-001, TASK-RULE-001, TASK-API-004, TASK-KB-002, TASK-LEGAL-002]
depends_on: [TASK-PLAT-001]
blocks: [TASK-RULE-001, TASK-API-004, TASK-PLAT-006, TASK-PLAT-009, TASK-AUTH-001]
new_paths:
  - db/migrations/0001_init_extensions.sql
  - db/migrations/0002_users.sql
  - db/migrations/0003_queries.sql
  - db/migrations/0004_charts.sql
  - db/migrations/0005_knowledge_patterns.sql
  - db/migrations/0006_reports.sql
  - db/migrations/0007_audit_logs.sql
  - db/migrations/0008_indexes_gin.sql
  - db/migrations/0009_rls_policies.sql
  - db/migrations/README.md
  - db/rls/session.md
  - db/tests/test_rls_isolation.sql
---

## §1 - Description (BCP-14 normative)

This task defines the PostgreSQL data tier (strategy 4.1) as forward-only, checked-in migrations: the six tables the platform persists - `users`, `queries`, `charts`, `knowledge_patterns`, `reports`, `audit_logs` - plus GIN indexes on their JSONB columns and fail-closed row-level security (RLS) for tenant/user isolation. It owns the schema and its migration history; it does NOT own how rows are written (TASK-API-004 persistence, TASK-AUTH-001 user creation) nor the cache (TASK-PLAT-006), though every writer targets this schema.

The migrations SHALL be forward-only and ordered (`NNNN_name.sql`), each idempotent enough to run once in sequence, with a documented, human-run apply path. The schema SHALL store the la so envelope (TASK-PLAT-002) in `charts.envelope` as `jsonb`, the rule conditions (TASK-RULE-001) in `knowledge_patterns.conditions` as `jsonb`, and the structured interpretation (TASK-RAG-003) in `reports.interpretation` as `jsonb`. Every JSONB column that is queried by containment SHALL carry a GIN index (`0008`).

RLS SHALL be fail-closed: every table that holds user-scoped data SHALL have `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`, and SHALL default to deny - no permissive policy means no row is visible. Access SHALL be granted only through explicit policies keyed on a per-request session variable (`app.current_user_id`, and `app.current_role` for the admin bypass), following the cyberos RLS pattern. A connection that has not set the session variable SHALL see zero rows, never all rows. Personal data (birth data, question text) is sensitive: `users.birth_data_encrypted` SHALL be stored as ciphertext (AES-256, encrypted by TASK-AUTH-001, opaque to the DB), the schema SHALL support soft-delete / erasure for VN PDPD and GDPR (TASK-LEGAL-002), and sensitive access is auditable via `audit_logs` (strategy 4.4, RISK-5).

## §2 - Why this design (rationale for humans)

The data tier holds exactly the data the risk register calls sensitive: birth data and question text (RISK-5). The single most dangerous default in a multi-user product is a query that forgets its `WHERE user_id = ...` and returns everyone's rows. RLS moves that guarantee from "every query remembers to filter" (which fails eventually) to "the database refuses to return another user's row regardless of the query" (which holds by construction). Making it fail-closed - deny by default, visible only through an explicit policy bound to a session variable the app sets per request - means a bug that forgets to set the variable leaks nothing, rather than leaking everything. This is the cyberos house pattern and it is non-negotiable here because the blast radius is personal divination data.

JSONB with GIN indexes is chosen for the three semi-structured columns (the chart envelope, the rule conditions, the interpretation) because their shape is owned by a contract elsewhere (TASK-PLAT-002, TASK-RULE-001, TASK-RAG-003) and evolves under versioning, not under DB migrations. Storing them as typed columns would duplicate those contracts in DDL and force a migration on every envelope change; storing them as `jsonb` with a GIN index keeps the queryability (containment, key existence) without pinning the DB to a shape another module owns. Forward-only migrations keep the schema history auditable and the production apply path boring.

## §3 - Contract (schema / indexes / RLS)

### Tables (columns abridged to the load-bearing set)

```sql
-- 0002_users.sql
create table users (
  id                     uuid primary key default gen_random_uuid(),
  email                  citext unique not null,
  password_hash          text,                       -- null for social-only (TASK-AUTH-001)
  display_name           text,
  tier                   text not null default 'free',   -- free|premium|enterprise|admin (TASK-AUTH-002)
  locale                 text not null default 'vi',
  birth_data_encrypted   bytea,                       -- AES-256 ciphertext, opaque here (RISK-5)
  created_at             timestamptz not null default now(),
  updated_at             timestamptz not null default now(),
  deleted_at             timestamptz                  -- soft-delete for erasure (TASK-LEGAL-002)
);

-- 0003_queries.sql
create table queries (
  id             uuid primary key default gen_random_uuid(),
  user_id        uuid not null references users(id) on delete cascade,
  datetime       text not null,      -- ISO local time of the question/event
  tz             text not null,      -- e.g. "+07:00"
  kinh_do        double precision,   -- longitude
  place          text,
  question_type  text not null,      -- loai_cau_hoi
  systems        text[] not null,    -- ["qimen"] | ["qimen","liuren"] | ["all"]
  persona_level  text not null default 'beginner',
  co_truong_phai jsonb,              -- school-flag overrides (else engine defaults)
  created_at     timestamptz not null default now()
);

-- 0004_charts.sql
create table charts (
  id             uuid primary key default gen_random_uuid(),
  query_id       uuid not null references queries(id) on delete cascade,
  user_id        uuid not null references users(id) on delete cascade,
  he             text not null,      -- luc_nham|ky_mon|thai_at
  envelope       jsonb not null,     -- the TASK-PLAT-002 la so envelope
  cache_key      text not null,      -- TASK-PLAT-002 cache key (TASK-PLAT-006 reads it)
  engine_version text not null,
  created_at     timestamptz not null default now()
);

-- 0005_knowledge_patterns.sql   (owned jointly with TASK-RULE-001; this task ships the table)
create table knowledge_patterns (
  id          uuid primary key default gen_random_uuid(),
  system      text not null,         -- qimen|liuren|taiyi|shared
  pattern_key text unique not null,  -- stable slug e.g. qimen_thanh_long_hoi_dau
  name        text not null,
  name_han    text,
  conditions  jsonb not null,        -- the TASK-RULE-001 condition DSL
  polarity    text,                  -- cat|hung|trung
  score       real,
  citations   jsonb not null default '[]',
  version     int not null default 1,
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

-- 0006_reports.sql
create table reports (
  id             uuid primary key default gen_random_uuid(),
  query_id       uuid not null references queries(id) on delete cascade,
  user_id        uuid not null references users(id) on delete cascade,
  interpretation jsonb not null,     -- the TASK-RAG-003 Interpretation object
  ai_disclosure  jsonb not null,     -- AIDisclosure block (mandatory)
  review_status  text not null default 'not_required',  -- pending|not_required|approved|rejected
  pdf_url        text,
  created_at     timestamptz not null default now()
);

-- 0007_audit_logs.sql
create table audit_logs (
  id            bigserial primary key,
  user_id       uuid references users(id) on delete set null,
  action        text not null,       -- e.g. chart.cast, report.read, user.erase
  resource_type text,
  resource_id   text,
  request_id    text,
  ip            inet,
  metadata      jsonb not null default '{}',
  created_at    timestamptz not null default now()
);
```

### GIN indexes (`0008_indexes_gin.sql`)

```sql
create index charts_envelope_gin        on charts             using gin (envelope       jsonb_path_ops);
create index patterns_conditions_gin    on knowledge_patterns using gin (conditions     jsonb_path_ops);
create index reports_interpretation_gin on reports            using gin (interpretation jsonb_path_ops);
-- plus btree helpers the hot paths need
create index charts_cache_key_idx on charts (cache_key);
create index queries_user_id_idx  on queries (user_id);
create index audit_user_time_idx  on audit_logs (user_id, created_at);
```

### RLS - fail-closed (`0009_rls_policies.sql`)

```sql
-- Applied to users, queries, charts, reports (and knowledge_patterns is read-mostly + admin-write).
alter table charts enable row level security;
alter table charts force row level security;   -- applies even to the table owner

-- Deny by default: with RLS enabled and no permissive policy, zero rows are visible.
-- Grant read/write only to rows owned by the request's user, resolved from a session GUC.
create policy charts_owner on charts
  using      (user_id = current_setting('app.current_user_id', true)::uuid)
  with check (user_id = current_setting('app.current_user_id', true)::uuid);

-- Admin bypass is an explicit, separate policy, never the default.
create policy charts_admin on charts to app_admin
  using (current_setting('app.current_role', true) = 'admin');
```

The app SHALL set `app.current_user_id` (and `app.current_role` where relevant) per request/transaction (`SET LOCAL`) from the authenticated principal (TASK-AUTH-001). `current_setting(..., true)` returns NULL when the GUC is unset, and `NULL::uuid = user_id` is never true, so an unset session sees no rows - the fail-closed property. `knowledge_patterns` is world-readable (seeded classical knowledge, TASK-KB-002) but admin/curator-write only.

## §4 - Acceptance criteria

1. Running `0001..0009` in order against an empty database produces the six tables with the columns above, the GIN indexes, and RLS enabled and forced on every user-scoped table.
2. Fail-closed proof: a connection that has NOT set `app.current_user_id` returns zero rows from `charts`, `queries`, and `reports` - never all rows.
3. Isolation proof: with `app.current_user_id = A`, selecting/updating a row owned by user B returns/affects nothing; user A sees only A's rows.
4. Admin bypass is explicit: only a principal with `app.current_role = 'admin'` (and role `app_admin`) sees cross-user rows, via the named admin policy, never via the default.
5. The three JSONB columns each have a GIN index, and a containment query (`envelope @> '{"he":"ky_mon"}'`) uses it (verified by `EXPLAIN`).
6. Migrations are forward-only and re-runnable in sequence on a fresh DB; the apply path is documented in `db/migrations/README.md`.
7. `users.birth_data_encrypted` is `bytea` (ciphertext), and the schema supports soft-delete (`deleted_at`) so erasure (TASK-LEGAL-002) is expressible.

## §5 - Verification

- `db/tests/test_rls_isolation.sql` (pgTAP or a scripted psql harness): sets `app.current_user_id` to A, inserts rows for A and B, asserts A sees only A's rows, asserts an unset session sees zero rows, asserts the admin policy is the only cross-user path. This is the RISK-5 gate and MUST run in CI against an ephemeral Postgres.
- An `EXPLAIN (ANALYZE)` check that each JSONB containment query hits its GIN index, not a seq scan.
- A migration test: apply `0001..0009` to a clean database in CI; assert table/column/index/policy presence via `information_schema` and `pg_policies`.
- Gates: the migration + RLS tests run in the CI `python`/integration lane (TASK-PLAT-001) against a service Postgres container; a failing isolation assertion fails the build.

## §6 - Implementation skeleton

1. `0001`: enable `pgcrypto` (for `gen_random_uuid`) and `citext`.
2. `0002..0007`: the six tables in dependency order (users first; queries/charts/reports reference users; audit_logs last).
3. `0008`: GIN indexes on the three JSONB columns plus the btree helpers.
4. `0009`: `enable`/`force` RLS on user-scoped tables; the owner policy and the explicit admin policy per table; create role `app_admin`.
5. `db/rls/session.md`: document the `SET LOCAL app.current_user_id` contract TASK-AUTH-001 / TASK-API-004 must honor per request.
6. `db/tests/test_rls_isolation.sql` + the CI wiring; `db/migrations/README.md` apply path.

## §7 - Dependencies

Depends on TASK-PLAT-001 (the repo and CI that run the migration tests). Blocks TASK-RULE-001 (the `knowledge_patterns` table and its `conditions` JSONB are this schema), TASK-API-004 (query/chart/report/audit persistence writes these tables and sets the RLS session variable), TASK-PLAT-006 (the Redis chart cache is keyed off `charts.cache_key`), TASK-PLAT-009 (backup/PITR/restore drill runs against this schema), and TASK-AUTH-001 (user rows and the encrypted birth-data column). Coordinates with TASK-LEGAL-002 (erasure/export operate on this schema) and TASK-PLAT-002 (the envelope stored in `charts.envelope`).

## §8 - Example payloads

```sql
-- per-request preamble the app runs inside the transaction (TASK-API-004 / TASK-AUTH-001)
set local app.current_user_id = '3f2a...-uuid';

-- a chart write; RLS check confirms user_id matches the session user
insert into charts (query_id, user_id, he, envelope, cache_key, engine_version)
values ('q-uuid', '3f2a...-uuid', 'ky_mon', '{"envelope_version":1, "he":"ky_mon", ...}'::jsonb,
        'ck_...', '0.1.0');

-- a containment read that uses the GIN index
select id from charts where envelope @> '{"he":"ky_mon"}'::jsonb;
```

## §9 - Open questions

- Migration tool: raw SQL files applied by a thin runner vs sqlx-migrate vs alembic vs an external tool (Flyway). Default: plain ordered SQL under `db/migrations/` with a documented psql apply path, so no ORM owns the schema and both the Rust and Python sides read the same DDL. Revisit if a team convention argues for a runner.
- "Tenant" scope at MVP: users are the isolation unit now; an org/tenant layer (Enterprise seats) is a later column (`org_id`) and an additional RLS clause. Default: user-level isolation now; reserve `org_id` for the Enterprise tier without a breaking migration (nullable add + policy extension).
- Vector storage location: pgvector in this Postgres vs a separate vector DB (strategy 4.1 lists Chroma/pgvector/Pinecone). Default: pgvector as an extension in this instance for MVP (TASK-RAG-001 owns the embedding tables); this task reserves the extension slot in `0001` if pgvector is chosen.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Fail-open RLS | RLS enabled but a permissive default policy exists, or `FORCE` omitted | forbidden; deny-by-default + FORCE; the isolation test asserts an unset session sees zero rows |
| Missing session GUC | app forgets `SET LOCAL app.current_user_id` | zero rows returned (fail-closed), never all rows; not a silent full-table read |
| Cross-user leak | a policy keyed on the wrong column | isolation test (user A vs user B) fails in CI before ship |
| Seq scan on JSONB | GIN index missing or wrong opclass | `EXPLAIN` check fails; add the `jsonb_path_ops` GIN index |
| Plaintext birth data | birth data stored unencrypted | forbidden; column is `bytea` ciphertext (AES-256 by TASK-AUTH-001), DB never sees plaintext |
| Irreversible delete blocks erasure | hard-delete only | soft-delete `deleted_at` supports the erasure/export contracts (TASK-LEGAL-002) |

## §11 - Notes

The RLS discipline is the point of this task: fail-closed, forced, deny-by-default, admin as an explicit policy - the same pattern cyberos uses, chosen because the blast radius here is personal divination data (RISK-5). Keep migrations forward-only and the schema shapes that another module owns (`envelope`, `conditions`, `interpretation`) as `jsonb` under GIN, so those contracts evolve under their own versioning rather than under DDL. The per-request `SET LOCAL app.current_user_id` contract is the seam TASK-AUTH-001 and TASK-API-004 must honor on every connection; document it in `db/rls/session.md` and treat a code path that talks to Postgres without setting it as a defect.
