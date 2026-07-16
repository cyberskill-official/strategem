# COV-027 implementation notes

## Landed

| artefact | path |
|----------|------|
| Local compose (build-from-source) | `deploy/compose/docker-compose.local.yml` |
| API Dockerfile | `deploy/docker/api.Dockerfile` (`/src` layout, `CAST_CLI=/src/cast-cli`) |
| Web Dockerfile | `deploy/docker/web.Dockerfile` |
| Runbook | `docs/deploy/local-docker-lmstudio.md` |
| deploy README pointer | `deploy/README.md` |
| Static contract tests | `packages/tamthuc_api/tests/test_compose_local_cov027.py` |

## Live dual-run (operator host)

Stack name `strategem-local` on alternate ports (host 8000 conflict):

- API `18000`, web `13000`, PG `15432`, Redis `16379`
- `/healthz` → `{"status":"ok"}`
- `/ready` → cast_cli present at `/src/cast-cli`, engine_mode `cast_cli`
- `POST /api/v1/calculate/qimen` → non-empty `charts.qimen.ban` (dia_ban/thien_ban/cuu_tinh/…)
- Two independent probe cycles recorded under operator scratch

## Tests

| suite | result |
|-------|--------|
| test_compose_local_cov027 (3) | pass |
| live dual health + cast | pass (see SCRATCH) |

## Status

`ready_to_review` — **HITL required**. Agent will not set `done`.
