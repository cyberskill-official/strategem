# Auth token contract (TASK-AUTH-001)

## Access token (JWT)

| Claim | Type | Notes |
|---|---|---|
| `sub` | string (UUID) | user id |
| `tier` | string | `free` / `premium` / `enterprise` / `admin` (TASK-AUTH-002) |
| `iat` | int | issued-at unix seconds |
| `exp` | int | expiry; default TTL 15 minutes |
| `jti` | string (UUID) | unique id |
| `typ` | string | always `access` |
| `iss` | string | `tamthuc-auth` (configurable) |

Signed with `TAMTHUC_AUTH_JWT_SECRET` (HS256). Verified by `tamthuc_auth.tokens.verify_access`.

## Refresh token (JWT)

| Claim | Type | Notes |
|---|---|---|
| `sub` | string | user id |
| `iat` / `exp` | int | default TTL 14 days |
| `jti` | string | revocation key |
| `typ` | string | always `refresh` |

On `/auth/refresh`, the presented refresh `jti` is revoked and a new pair is issued (rotation).

## Endpoints

See TASK-AUTH-001 §3. Bearer scheme on `/auth/me`.

AUTH-001 foundations also mount (enumeration-safe where noted):

| Method | Path | Notes |
|---|---|---|
| POST | `/auth/verify/request` | email body; generic OK |
| POST | `/auth/verify/confirm` | `{token}` |
| POST | `/auth/password-reset/request` | email body; generic OK |
| POST | `/auth/password-reset/confirm` | `{token, new_password}`; revokes all refresh families |
| POST | `/auth/logout` | `{refresh}` — revoke family/jti; idempotent |
| GET | `/auth/sessions` | Bearer — list active refresh families |
| POST | `/auth/sessions/{id}/revoke` | Bearer — revoke one family |
| POST | `/auth/sessions/revoke-all` | Bearer — revoke all families for subject |
| POST | `/auth/dsar/export` | Bearer + fresh auth window |
| POST | `/auth/dsar/erase` | Bearer + fresh auth window |

Refresh JWTs carry optional `fid` (family id). Rotation updates `current_jti` in
`refresh_token_families`; presenting a non-current jti for an active family is
treated as reuse and revokes the whole family.

Web BFF (`apps/web/app/api/auth/*`): refresh stays in HttpOnly cookie `tamthuc_refresh`;
access returned in JSON. Cookie-bearing `/api/auth/refresh` requires a matching
`Origin` or `Referer` (set `WEB_ORIGIN` / `AUTH_CSRF_ORIGINS` in deploy). Operator
email HITL: `docs/deploy/auth-email-resend.md`.

Durable stores (when `DATABASE_URL` + postgres auth backend): `email_tokens`,
`refresh_token_families`, plus existing `refresh_token_revocations`.

## Errors

All failures use:

```json
{ "error": { "code": "<code>", "message": "authentication failed" } }
```

Unknown email and wrong password share the same message (no account enumeration).
