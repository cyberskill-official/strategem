# Production-readiness code remainings (2026-09)

This PR batch closes the implementable *code* gaps called out after AUTH-001 (#28/#29)
and the earlier kill-switch / CD / DB / review work. Operator HITL stays separate.

## Shipped in code

| ID / gap | Change |
|---|---|
| D-MIG-001 | Python migrator: SHA-256 checksum ledger, `pg_advisory_lock`, dirty-state fail-closed; `deploy/vps/migrate.sh` delegates to `python -m db_schema.migrate` |
| D-API-001 (partial) | Real Redis daily counters (`REDIS_URL`), conservative local fallback, trusted-proxy IP (`TRUSTED_PROXY_COUNT`), meter auth + calculate paths |
| `/docs` lockdown | OpenAPI `/docs` `/redoc` `/openapi.json` off outside local/test unless `ENABLE_API_DOCS=1` |
| AUTH-001 UI | Session list / revoke on `/manage/settings` |
| CSRF | Double-submit `tamthuc_csrf` + `X-CSRF-Token` on cookie refresh/logout BFF (in addition to Origin/Referer) |
| Security headers | API middleware applies `security_headers()` on responses |
| Readiness | `/ready` reports `email_configured`, `api_docs_enabled`, `redis_configured` (booleans only) |
| PayOS | Remains disabled outside local/test (unchanged) |

## Operator-only / deferred (not claimed done)

- Resend domain DNS + API keys → F03–F05 production email (fail-closed without secrets)
- Redis host provisioning + `REDIS_URL` on VPS/staging
- Supabase PITR / restore drill evidence
- GitHub Environment reviewers already documented in D-CD-001 (#25); re-attest as needed
- Counsel commercial values for future PayOS
- AUTH-002 real OIDC
- Large product tracks still open in the completion plan (EDU/KB/ADMIN/PRIV/I18N/A11Y/OBS/REL/CORE oracle, etc.) — out of scope for this production-readiness code slice
- Production deploy / merge

## Verify locally

```bash
.venv/bin/python -m pytest packages/db_schema/tests packages/tamthuc_api/tests/test_redis_ratelimit.py packages/tamthuc_api/tests/test_docs_lockdown.py packages/tamthuc_api/tests/test_ratelimit.py -q
pnpm --filter web test
```
