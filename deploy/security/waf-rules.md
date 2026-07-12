# WAF rules (edge)

- Rate-limit bursts per IP and per JWT subject.
- Block known SQLi/XSS signatures on `/auth/*` and `/api/*`.
- Geo / bot challenges optional at Enterprise tier.
