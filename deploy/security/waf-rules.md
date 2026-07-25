# WAF rules (planned — not deployed)

> **Status:** sketch only. Strategem does **not** currently run a managed WAF in front of the
> VPS API. Treat this as a backlog for TASK-PLAT-007 / edge hardening, not as evidence of an
> active control. Live DoS controls today: app rate limits + host firewall.

When an edge WAF is wired:

- Rate-limit bursts per IP and per JWT subject.
- Block known SQLi/XSS signatures on `/auth/*` and `/api/*`.
- Geo / bot challenges optional at Enterprise tier.
