---
artefact: edge-case-matrix@1
fr_id: FR-PLAT-003
---

# Edge-case matrix — FR-PLAT-003

| id | category | case | expected | coverage |
|---|---|---|---|---|
| EC-1 | NULL/empty | unset `app.current_user_id` | 0 rows from charts/queries/reports | `test_fail_closed_unset_guc` |
| EC-2 | bounds | two users A/B isolation | A never sees B | `test_isolation_user_a_cannot_see_b` |
| EC-3 | concurrent | N/A at schema layer | app sets SET LOCAL per txn | `db/rls/session.md` |
| EC-4 | malformed | invalid UUID GUC cast | expression fails closed / no leak | owner policy uses `::uuid` |
| EC-5 | security | fail-open RLS (no FORCE) | forbidden | `test_schema_objects_exist` asserts FORCE |
| EC-6 | security | admin only via explicit policy | cross-user only with role+GUC | `test_admin_bypass_explicit` |
| EC-7 | security | plaintext birth data | column is `bytea` only | `test_schema_objects_exist` |
| EC-8 | degradation | GIN missing | EXPLAIN/index inventory fails | `test_gin_index_used_for_containment` + unit |
| EC-9 | soft-delete | erasure support | `users.deleted_at` present | unit + schema test |

`total_rows: 9` (≥8 for MUST).
