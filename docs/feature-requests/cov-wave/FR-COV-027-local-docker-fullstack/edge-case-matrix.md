# edge-case-matrix@1 — COV-027

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | CONFIG | compose uses build: not GHCR | no ghcr.io refs | test_local_compose_builds_not_ghcr |
| E2 | CONFIG | CAST_CLI + READY_REQUIRE_CAST_CLI | /ready 200 when CLI present | docker dual probe + ready checks |
| E3 | DEGRADATION | cast-cli missing | /ready fails closed when required | READY_REQUIRE_CAST_CLI=1 |
| E4 | NETWORK | web → API base | NEXT_PUBLIC_API_BASE documented | compose web args + runbook |
| E5 | DATA | Postgres DATABASE_URL set | app starts with healthy DB | compose postgres healthcheck |
| E6 | SECURITY | No prod secrets required | local JWT default documented | compose TAMTHUC_AUTH_JWT_SECRET |
| E7 | OPS | Dual compose boot | two healthz+ready+cast cycles | docker-dual-probe + cast dual log |
| E8 | DOCS | One-command runbook | local-docker-lmstudio.md present | test_local_runbook_exists |
