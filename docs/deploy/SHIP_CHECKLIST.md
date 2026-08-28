# Ship checklist — batch ops (post-FR complete)

All product tasks are **done** (BACKLOG: 93). Remaining work is **operator linking**, not code.

## LEGAL-004 counsel gate (RISK-4)

**Status:** `approved` (2026-07-26). Re-run the check after material copy /
positioning / monetization changes; re-open the gate if the re-review trigger fires.

```bash
bash scripts/check-counsel-signoff.sh
# or: just counsel-gate
# or: just ship-ready   # includes counsel-gate + machine gates
```

| Artifact | Path |
|---|---|
| Machine status | `docs/legal/vn-legal-review/gate-status.json` |
| Sign-off record | `docs/legal/vn-legal-review/counsel-signoff-record.md` |
| Pre-launch checklist | `docs/legal/vn-legal-review/checklist.md` |
| Operator how-to | `docs/legal/vn-legal-review/operator-runbook.md` |

Agents must not invent an approval. Current expected result: script **exits 0**.

## Pre-flight (local)

For **public launch** pre-flight, confirm counsel gate still green:

```bash
# LEGAL-004 — must exit 0 while verdict=approved
bash scripts/check-counsel-signoff.sh

# Rust floor
bash .cyberos/cuo/gates/run-gates.sh

# Web
cd apps/web && pnpm --filter web test

# API unit
.venv/bin/python -m pytest packages/tamthuc_api/tests -q

# Cast CLI with full LN plates
export CAST_CLI=$PWD/target/debug/cast-cli   # or target/release after cargo build --release
echo '{"system":"liuren","lich_phap":{"datetime":"2004-01-01T10:30:00","tz":"+07:00","kinh_do":105.85}}' \
  | "$CAST_CLI" | python3 -c 'import json,sys; b=json.load(sys.stdin)["ban"]; assert "thien_dia_ban" in b'
```

## Link surfaces (manual secrets — do not commit)

| # | Surface | Action |
|---|---------|--------|
| 1 | **Supabase** | Create project; migrate with privileged `DATABASE_URL_MIGRATE`; set API `DATABASE_URL` to `strategem_app` (D-DB-001); see `docs/deploy/supabase.md` |
| 1b | **Local Docker Postgres** | `docker compose -f deploy/compose/docker-compose.local.yml up -d postgres migrate` (API uses `strategem_app`; migrate uses `postgres`) |
| 2 | **VPS API** | Provision host; copy `deploy/vps/.env.example` → `.env`; set `CAST_CLI` in image; `deploy/vps/deploy.sh` |
| 3 | **Vercel web** | Link monorepo; set `NEXT_PUBLIC_API_BASE=https://api.<domain>`; deploy |
| 4 | **CORS** | VPS allows Vercel production + preview origins |
| 5 | **Smoke** | Browser cast Kỳ Môn / Lục Nhâm / Thái Ất → results → pin → history → report PDF |

## Env inventory

- Vercel: `NEXT_PUBLIC_API_BASE`, optional `API_URL`
- VPS: `DATABASE_URL`, JWT secrets, `CAST_CLI`, CORS origins
- Supabase: connection string only to VPS (never to browser)

## Readiness probes (API)

```bash
# Liveness
curl -sS "$API_BASE/healthz"

# Readiness — cast-cli diagnostics
curl -sS "$API_BASE/ready"
# Production (optional strict): READY_REQUIRE_CAST_CLI=1 → 503 if CLI missing
```

## Git hooks (local)

```bash
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
# runs ruff format/check on staged py + eslint on web when those paths are staged
```

## Done when

- [x] **LEGAL-004 counsel gate green** (`just counsel-gate` exit 0) — recorded approved 2026-07-26; re-checked 2026-07-28 (`verdict=approved`, exit 0)
- [x] Gates green on `main` — SHA `63029d1` (2026-07-28): [CI](https://github.com/cyberskill-official/strategem/actions/runs/30289903496) success, [product-journeys](https://github.com/cyberskill-official/strategem/actions/runs/30289903464) success, [Security scan](https://github.com/cyberskill-official/strategem/actions/runs/30289903722) success
- [x] API `healthz` 200 on VPS — `curl -fsS https://api.strategem.cyberskill.world/healthz` → `{"status":"ok"}` HTTP 200 (2026-07-28); `/ready` also 200 with cast-cli + llm ok
- [ ] Web production cast against live API — homepage `https://strategem-sepia.vercel.app/` returns 200; full cast→results→pin journey **not** re-attested this pass
- [ ] Migrations applied; RLS fail-closed still holds — local `.local/migrate.log` shows a failed resolve of the Supabase host (not a VPS ledger dump); **do not treat as applied** without operator DB attestation

Staging / private ops linking may proceed without counsel approval. **Public
marketing launch and store submission may not.**

**Hold (unchanged this pass):** PayOS live credentials, durable CF API token rotation, VPS password rotation, counsel firm-name polish.

## Staging (COV-020)

See `docs/deploy/staging-runbook.md` and `bash scripts/smoke-staging.sh`.
