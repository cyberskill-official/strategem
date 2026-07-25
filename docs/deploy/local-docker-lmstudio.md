# Local full stack: Docker + LM Studio

Enterprise local path for Strategem (**COV-027**, **COV-028**, Phase 4). No cloud keys required for cast + optional local interpretation.

## Prerequisites

| Tool | Role |
|------|------|
| Docker Desktop / Engine + Compose v2 | Postgres, migrate, API, web |
| [LM Studio](https://lmstudio.ai/) (host) | OpenAI-compatible local model at `:1234` |
| Optional: host `cast-cli` + `uv` | Dev without Docker |

## One command

```bash
# From repo root — free ports if host already uses 8000/3000
export LOCAL_API_PORT=18000 LOCAL_WEB_PORT=13000 LOCAL_PG_PORT=15432
export NEXT_PUBLIC_API_BASE=http://127.0.0.1:18000
export API_URL=http://api:8000
export LLM_MODEL=your-exact-lm-studio-model-id

just local-up
# prints health matrix: postgres, api /healthz+/ready, web, LM Studio probe
```

Tear down: `just local-down`.

## What `local-up` does

1. `docker compose -f deploy/compose/docker-compose.local.yml up --build -d`
2. **migrate** one-shot runs `python -m db_schema.migrate` before API starts
3. API waits on migrate success; web waits on API healthcheck
4. Prints readiness matrix (including optional host LM Studio)

## LM Studio (host)

1. Install LM Studio and load an instruct model that follows JSON instructions.
2. Start **Local Server** (OpenAI-compatible). Default: `http://127.0.0.1:1234/v1`.
3. Copy the **exact model id** from the UI → `LLM_MODEL` (do not leave `local-model` unless that is the real id).

```bash
curl -sS http://127.0.0.1:1234/v1/models | head
```

Compose reaches the host via `host.docker.internal` (`LLM_BASE_URL` default).

### Readiness vs degraded UX

| Flag | Behaviour |
|------|-----------|
| (default) | `/ready` stays OK when LM Studio is down; interpretation returns **explicit degraded** disclosure (`degraded: true`, rule-based/template fallback) — not silent fake RAG success |
| `READY_REQUIRE_LLM=1` | `/ready` returns **503** when the LLM backend is unreachable (strict local gate) |

## Compose services

| Service | Role |
|---------|------|
| `postgres` | App DB (healthchecked) |
| `migrate` | Ledgered migrations; `service_completed_successfully` |
| `api` | FastAPI + cast-cli; `ENV=development`; `PAYMENTS_MODE=mock` |
| `web` | Next.js; `API_URL=http://api:8000` |

Redis is **not** in the local compose (avoids unused-service false confidence). Rate limits use the in-process limiter locally.

## Payments (mock)

Local default `PAYMENTS_MODE=mock` — no PayOS credentials required. Pricing UI can complete mock checkout; webhook fail-closed still applies when `PAYOS_CHECKSUM_KEY` is set without mock mode.

## Auth secrets (local)

Compose sets development JWT + master key placeholders. Override for Postgres-backed auth stores as needed. Never reuse these values outside `ENV=development`.

## Dual-run check

Stop stack, bring up again, re-check health + cast. Two consecutive boots are the enterprise gate.

## Cast path

```bash
curl -sS "http://127.0.0.1:${LOCAL_API_PORT:-8000}/ready"
# Cast via API; provenance.engine_source should be cast_cli when CLI present
```

## Host-only API (no Docker)

```bash
export CAST_CLI="$PWD/target/release/cast-cli"
export LLM_BACKEND=openai_compatible
export LLM_BASE_URL=http://127.0.0.1:1234/v1
export LLM_MODEL=your-model-id
uv run python -m tamthuc_api
```

## Staging vs local

| File | Purpose |
|------|---------|
| `deploy/compose/docker-compose.local.yml` | **Build from source** — developer / enterprise local |
| `deploy/compose/docker-compose.staging.yml` | Pulls **GHCR** images — staging bootstrap |

## Tear down

```bash
just local-down
# or: docker compose -f deploy/compose/docker-compose.local.yml down -v
```
