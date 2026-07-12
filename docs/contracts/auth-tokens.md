# Auth token contract (FR-AUTH-001)

## Access token (JWT)

| Claim | Type | Notes |
|---|---|---|
| `sub` | string (UUID) | user id |
| `tier` | string | `free` / `premium` / `enterprise` / `admin` (FR-AUTH-002) |
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

See FR-AUTH-001 §3. Bearer scheme on `/auth/me`.

## Errors

All failures use:

```json
{ "error": { "code": "<code>", "message": "authentication failed" } }
```

Unknown email and wrong password share the same message (no account enumeration).
