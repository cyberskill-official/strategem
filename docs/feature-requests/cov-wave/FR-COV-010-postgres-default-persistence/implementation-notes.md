# COV-010 implementation notes

## Landed

| artefact | path |
|----------|------|
| Migration | `db/migrations/0010_app_query_store.sql` |
| PgQueryStore | `packages/tamthuc_api/src/tamthuc_api/pg_store.py` |
| PersistenceService.from_env | `packages/tamthuc_api/src/tamthuc_api/persistence.py` |
| create_app wiring | `packages/tamthuc_api/src/tamthuc_api/app.py` |
| Orchestrator re-save | uses `persistence.save_result` (PG-safe) |
| Tests | `packages/tamthuc_api/tests/test_postgres_persist_cov010.py` |
| Docs | `docs/deploy/local-docker-lmstudio.md` §5, `SHIP_CHECKLIST.md` |

## Behaviour

- `DATABASE_URL` present → cast payloads land in `app_query_store` and survive process restart (new PersistenceService instance).
- No URL + non-prod → in-memory (dev/test).
- `APP_ENV=production` without URL → fail closed unless `ALLOW_MEMORY_PERSISTENCE=1`.

## Tests

5/5 green against local compose Postgres `:15432`. Evidence: `{SCRATCH}/cov010-tests.log`.

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
