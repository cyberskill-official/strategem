# RLS session contract (TASK-PLAT-003)

Fail-closed row-level security is the RISK-5 gate for personal divination data. This document is the seam TASK-AUTH-001 and TASK-API-004 **must** honour on every Postgres transaction that touches user-scoped tables.

## GUCs

| Setting | Type | Meaning |
|---|---|---|
| `app.current_user_id` | text UUID | Authenticated principal; policies compare to `users.id` / `*.user_id` |
| `app.current_role` | text | When `'admin'` **and** the DB role is `app_admin`, the admin bypass policy applies |

Use `SET LOCAL` so the values are transaction-scoped and never leak across pool checkouts:

```sql
BEGIN;
SET LOCAL app.current_user_id = '3f2a0000-0000-4000-8000-0000000000aa';
-- optional admin path (only after privilege check in app code):
-- SET LOCAL app.current_role = 'admin';
-- SET ROLE app_admin;

-- business SQL here

COMMIT;  -- or ROLLBACK; LOCAL settings drop with the transaction
```

## Fail-closed property

Policies use:

```sql
current_setting('app.current_user_id', true)::uuid
```

The second argument `true` means "missing GUC → NULL, do not error".  
`NULL::uuid = user_id` is never true, so an unset session sees **zero rows**. This is intentional. A code path that talks to Postgres without setting the GUC is a **defect**, not a full-table read.

## Roles

| Role | Purpose |
|---|---|
| `app_user` | Normal application connections (owner policies) |
| `app_admin` | Explicit admin bypass policies only |

Table owner still has `FORCE ROW LEVEL SECURITY`, so superuser-less owners cannot silently bypass. Superuser (migration apply, CI setup) can bypass RLS for bootstrap; production app credentials must **not** be superuser.

## Tables

| Table | Policy model |
|---|---|
| `users`, `queries`, `charts`, `reports`, `audit_logs`, `app_query_store` | Owner (`user_id` / `id` match) + admin bypass |
| `knowledge_patterns` | `SELECT` world-readable; write only via `app_admin` + `app.current_role = 'admin'` |

## Anti-patterns (forbidden)

1. Connection pool that reuses a session without clearing / re-setting GUCs.
2. Setting `app.current_user_id` once at process start and never per request.
3. Relying on application `WHERE user_id = ...` without RLS (RLS is the backstop).
4. Granting superuser to the API role "for convenience".
5. A default permissive policy that makes unset sessions see everything.

## Verification

`db/tests/test_rls_isolation.sql` and `packages/db_schema` assert:

1. Unset GUC → 0 rows from `charts` / `queries` / `reports`.
2. User A cannot see user B's rows.
3. Admin path is only via the named admin policy + role.
