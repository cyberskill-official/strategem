# Auth email (Resend) — operator HITL

**Task:** TASK-AUTH-001 (AUTH-001 foundations)  
**Status:** Code supports FakeEmailSender locally and Resend when configured.  
**Not done:** Production verification / reset / F03–F05 acceptance until a human configures Resend.

## Why HITL

Transactional email (verify, password reset) must leave the platform. Agents must not invent a sending domain or claim F03–F05 complete without a real Resend project + verified domain + from-address.

## Local / test (no secrets)

| Env | Behavior |
|---|---|
| `ENV` / `APP_ENV` empty, `development`, `dev`, or `test` | `FakeEmailSender` (in-memory; no network) |
| `AUTH_EMAIL_FAKE=1` or `ALLOW_FAKE_EMAIL=1` | Force fake even if `ENV` looks like staging |
| Unit/API tests | Fake by default |

Register → verify and password-reset flows work end-to-end against the fake sink.

## Production / staging (fail closed)

Without `RESEND_API_KEY` + from-address, endpoints that send mail return **503** `email_not_configured`:

- `POST /auth/register`
- `POST /auth/verify/request`
- `POST /auth/password-reset/request`

## Operator checklist (Resend)

1. Create or select a Resend account for this environment.
2. Add and **verify** the sending domain (DNS: SPF / DKIM as Resend instructs).
3. Choose a from-address on that domain (e.g. `noreply@your-domain`).
4. Create an API key with send permission; store it only in the secret store / host env — never in git.
5. Set on the API host (staging then production):

| Variable | Purpose |
|---|---|
| `RESEND_API_KEY` | Resend API key |
| `RESEND_FROM` (or `RESEND_FROM_ADDRESS`) | Verified from-address |

6. Smoke: register a throwaway inbox; confirm verify email arrives; confirm reset email arrives.
7. Record the HITL verdict in the task review / status hub (human acceptance gates). Do **not** mark CyberOS tasks `done` from an agent.

## Session cookies (BFF)

Next.js BFF under `apps/web/app/api/auth/`:

- Login / signup set `tamthuc_refresh` as **HttpOnly**, `SameSite=Lax`, `Secure` in production.
- `POST /api/auth/refresh` rotates using the cookie; returns **access** in JSON only.
- `POST /api/auth/logout` revokes on the API (best-effort) and clears the cookie.

Access tokens stay in memory / `sessionStorage` (short-lived Bearer). Refresh must not be readable by page JS.

## Deferred (follow-up slices)

- Durable email-token table (today: process-local `EmailTokenStore` unless extended).
- Refresh-family rows, session list / revoke-one / revoke-all UI.
- CSRF / Origin hardening matrix for cookie refresh.
- Rich HTML templates + deep links with branded URLs.
- AUTH-002 real Google/Apple OIDC (still kill-switched outside local/test).
