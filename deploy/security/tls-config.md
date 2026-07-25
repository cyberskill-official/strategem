# TLS (edge / Caddy)

- Minimum TLS **1.3** at the edge (Caddy defaults; no 1.0/1.1/1.2 for user-data routes).
- HSTS enabled via Caddy `header` (`Strict-Transport-Security`) — see `deploy/vps/Caddyfile`.
- Also set at the edge: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
  `Referrer-Policy: strict-origin-when-cross-origin`.
- **CSP** is intentionally deferred (follow-up) until API + Vercel web routes are stable.
- Certificates via Caddy ACME / secret manager (TASK-PLAT-007 secrets.md).

## What is not deployed yet

- There is **no live WAF** in front of the VPS API today. `deploy/security/waf-rules.md` is a
  **planned** edge rule sketch, not an enforced control. DoS mitigation currently relies on
  application rate limits (TASK-API-003) plus host/network controls — not a managed WAF product.
