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
| POST | `/auth/password-reset/confirm` | `{token, new_password}`; revokes refresh jtis when provided |
| POST | `/auth/logout` | `{refresh}` — revoke jti; idempotent |
| POST | `/auth/dsar/export` | Bearer + fresh auth window |
| POST | `/auth/dsar/erase` | Bearer + fresh auth window |

Web BFF (`apps/web/app/api/auth/*`): refresh stays in HttpOnly cookie `tamthuc_refresh`; access returned in JSON. Operator email HITL: `docs/deploy/auth-email-resend.md`.

## Errors

All failures use:

```json
{ "error": { "code": "<code>", "message": "authentication failed" } }
```

Unknown email and wrong password share the same message (no account enumeration).
