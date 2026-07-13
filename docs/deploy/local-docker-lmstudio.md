# Local full stack: Docker + LMStudio

Enterprise local path for Strategem (**COV-027**, **COV-028**). No cloud keys required for cast + optional local interpretation.

## Prerequisites

| Tool | Role |
|------|------|
| Docker Desktop / Engine + Compose v2 | Postgres, Redis, API, web |
| [LMStudio](https://lmstudio.ai/) (host) | OpenAI-compatible local model at `:1234` |
| Optional: host `cast-cli` + `uv` | Dev without Docker |

## 1. LMStudio (host)

1. Install LMStudio and load any instruct model (GGUF) that follows JSON instructions.
2. Start **Local Server** (OpenAI-compatible). Default base URL: `http://127.0.0.1:1234/v1`.
3. Note the model id shown in the server UI → set `LLM_MODEL`.

```bash
# Probe
curl -sS http://127.0.0.1:1234/v1/models | head
```

## 2. Docker Compose (build from source)

```bash
# From repo root — free ports if host already uses 8000/3000
export LOCAL_API_PORT=18000 LOCAL_WEB_PORT=13000 LOCAL_PG_PORT=15432
# Browser (host) hits published API port:
export NEXT_PUBLIC_API_BASE=http://127.0.0.1:18000
# Web container server-side proxy (login/signup route handlers + rewrites):
export API_URL=http://api:8000
export LLM_BACKEND=openai_compatible
export LLM_BASE_URL=http://host.docker.internal:1234/v1
export LLM_MODEL=your-model-id

docker compose -f deploy/compose/docker-compose.local.yml up --build -d

curl -sS "http://127.0.0.1:${LOCAL_API_PORT:-8000}/healthz"
curl -sS "http://127.0.0.1:${LOCAL_API_PORT:-8000}/ready"
```

API image builds `cast-cli` and runs `python -m tamthuc_api` with `CAST_CLI=/src/cast-cli` and `READY_REQUIRE_CAST_CLI=1`.

### Dual-run check

Stop stack, bring up again, re-check health + cast (see below). Two consecutive boots are the enterprise gate.

## 3. Cast path

```bash
# Prefer API once COV product routes are live; host CLI also works:
export CAST_CLI="$PWD/target/release/cast-cli"
"$CAST_CLI" --help   # or documented subcommand for KM/LN/TA
```

Representative systems: **KM** (kỳ môn / qimen), **LN** (lục nhâm / liuren), **TA** (thái ất / taiyi).

## 4. LLM env (API)

| Variable | Default | Meaning |
|----------|---------|---------|
| `LLM_BACKEND` | `stub` (CI) / `openai_compatible` (local compose) | `stub` \| `openai_compatible` \| `lmstudio` \| `off` |
| `LLM_BASE_URL` | `http://127.0.0.1:1234/v1` | LMStudio base (append `/chat/completions`) |
| `LLM_MODEL` | `local-model` | Model id in LMStudio |
| `LLM_API_KEY` | empty | Optional bearer |
| `LLM_TIMEOUT_S` | `60` | Request timeout |

When LMStudio is down, interpretation uses the **template / degraded** path (`tamthuc_rag` fallback) with an honest non-LLM disclosure — never fake live RAG claims.

### Host-only API (no Docker)

```bash
export CAST_CLI="$PWD/target/release/cast-cli"
export LLM_BACKEND=openai_compatible
export LLM_BASE_URL=http://127.0.0.1:1234/v1
export LLM_MODEL=your-model-id
uv run python -m tamthuc_api
```

## 5. Postgres persistence (COV-010)

Local compose sets `DATABASE_URL` on the API service. Apply migrations (including `0010_app_query_store.sql`) once per empty database:

```bash
export DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:${LOCAL_PG_PORT:-5432}/strategem
# from repo root
PYTHONPATH=packages/db_schema/src python -m db_schema.migrate
# or: uv run --package db_schema python -m db_schema.migrate
```

Without `DATABASE_URL`, the API uses in-memory persistence (dev/test). With `APP_ENV=production` and no `DATABASE_URL`, the API **fails closed** unless `ALLOW_MEMORY_PERSISTENCE=1`.

Cast → `GET /api/v1/queries/{query_id}` must return the same payload after API process restart when Postgres is configured.

## 6. Staging vs local

| File | Purpose |
|------|---------|
| `deploy/compose/docker-compose.local.yml` | **Build from source** — developer / enterprise local |
| `deploy/compose/docker-compose.staging.yml` | Pulls **GHCR** images — staging bootstrap |

## 6. Tear down

```bash
docker compose -f deploy/compose/docker-compose.local.yml down -v
```
