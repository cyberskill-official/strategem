---
id: FR-AUTH-001
title: "Auth and user identity - JWT access + refresh, email/password and Google/Apple OIDC social login, user profile, birth_data AES-256-GCM encrypted at rest, email verification hook"
module: AUTH
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 14
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-36, strategy 4.4, strategy RISK-5]
related_frs: [FR-AUTH-002, FR-AUTH-003, FR-AUTH-004, FR-API-001, FR-API-004, FR-PLAT-003, FR-PLAT-007, FR-LEGAL-002]
depends_on: [FR-PLAT-001]
blocks: [FR-AUTH-002, FR-AUTH-003, FR-AUTH-004, FR-API-001, FR-LEGAL-002]
new_paths:
  - packages/tamthuc_auth/pyproject.toml
  - packages/tamthuc_auth/tamthuc_auth/__init__.py
  - packages/tamthuc_auth/tamthuc_auth/models.py
  - packages/tamthuc_auth/tamthuc_auth/passwords.py
  - packages/tamthuc_auth/tamthuc_auth/tokens.py
  - packages/tamthuc_auth/tamthuc_auth/social.py
  - packages/tamthuc_auth/tamthuc_auth/crypto.py
  - packages/tamthuc_auth/tamthuc_auth/routes.py
  - packages/tamthuc_auth/tamthuc_auth/deps.py
  - packages/tamthuc_auth/tamthuc_auth/config.py
  - packages/tamthuc_auth/migrations/0001_users.sql
  - packages/tamthuc_auth/tests/test_auth.py
  - packages/tamthuc_auth/tests/test_crypto.py
  - docs/contracts/auth-tokens.md
---

## §1 - Description (BCP-14 normative)

This FR builds the identity layer: user registration and login, JWT-based session tokens, social login, the user profile that holds sensitive birth_data, and the encryption that protects that data at rest. It is the birth of the `tamthuc_auth` Python package. It owns the `users` table shape and the token and crypto primitives; it does NOT own tier permissions or rate-limit quotas (FR-AUTH-002) nor the DSAR export/erasure flows (FR-AUTH-004).

Authentication SHALL issue a short-lived JWT access token and a longer-lived refresh token on successful login. The API SHALL support three login methods: email plus password, Google OIDC, and Apple OIDC. Passwords SHALL be hashed with a memory-hard algorithm (argon2 via passlib), never stored or logged in plaintext. JWTs SHALL be signed and verified with python-jose; the access token SHALL carry `sub` (user id), `tier` (from FR-AUTH-002, defaulting to Free), `iat`, `exp`, and a `jti`; the refresh token SHALL be independently revocable. Social login SHALL be handled through Authlib against the provider's OIDC discovery, verifying the provider id token before provisioning or linking a local user (just-in-time provisioning on first social login, linked to an existing email where one matches).

The user profile SHALL hold `birth_data` (date, time, place, and derived coordinates for chart casting) as sensitive personal data. `birth_data` SHALL be encrypted at rest with AES-256-GCM using a key that is never stored in the database (envelope encryption: a per-record data key wrapped by a KMS or an application master key held outside the DB). Personal data SHALL be TLS-protected in transit (enforced at the platform edge, FR-PLAT-007), and every sensitive read or write of `birth_data` SHALL be auditable (the audit row is written by FR-API-004). This is the AUTH half of RISK-5.

Registration SHALL create an unverified user and trigger an email-verification flow whose token issuance and confirmation endpoint are completed in FR-AUTH-003; this FR SHALL emit the verification event and mark `email_verified=false` so the P0 path is verification-ready. All auth failures SHALL return the structured error envelope (FR-API-001) with a generic message that does not reveal whether an email exists.

## §2 - Why this design (rationale for humans)

Birth data is the crown-jewel sensitivity of this product. A person's date, time, and place of birth is precisely the input a divination platform needs and precisely the data that, leaked, is both privately harmful and legally exposing under VN PDPD and GDPR (RISK-5, strategy 4.4). Encrypting it at rest with a key held outside the database means a database dump alone does not disclose it; envelope encryption with a wrapped per-record key means key rotation does not require re-encrypting every row by hand. This is not gold-plating - it is the minimum posture for handling this category of data, and the whole platform's legal footing (strategy 7) rests on it.

JWT plus refresh is the standard the Grok backend spec calls for (Grok-36), and it fits the split architecture: the stateless access token lets the FastAPI gateway authorize a request without a session lookup on the hot path, while the revocable refresh token gives back the control a pure-stateless design loses (a compromised session can be cut). Social login through Authlib against OIDC discovery, verifying the provider id token rather than trusting a client-passed profile, closes the most common social-login hole. Generic auth-failure messages avoid the account-enumeration leak that specific "no such user" versus "wrong password" responses create.

## §3 - Contract (schema / API / types)

### users table shape (`packages/tamthuc_auth/migrations/0001_users.sql`; owned here, run by the PLAT migration runner)

| Column | Type | Notes |
|---|---|---|
| id | uuid PK | |
| email | citext unique | unique index; case-insensitive |
| password_hash | text | argon2; null for social-only accounts |
| birth_data | jsonb | AES-256-GCM ciphertext envelope; never plaintext at rest |
| preferences | jsonb | language, default systems, school-flag defaults |
| email_verified | boolean | default false; set by FR-AUTH-003 |
| tier | text | enum Free/Premium/Enterprise/Admin (FR-AUTH-002); default Free |
| created_at | timestamptz | |
| updated_at | timestamptz | |

This is the `users` table the master catalog assigns to FR-PLAT-003; AUTH is its natural owner, so the DDL lives here and PLAT-003 runs it as part of the umbrella migration set (see section 7).

### Token model (`tamthuc_auth/tokens.py`, contract in `docs/contracts/auth-tokens.md`)

```python
class AccessClaims(BaseModel):
    sub: str; tier: str; iat: int; exp: int; jti: str        # short TTL (e.g. 15 min)

def issue_access(user_id: str, tier: str) -> str: ...        # python-jose, signed
def issue_refresh(user_id: str) -> str: ...                  # long TTL, revocable by jti
def verify_access(token: str) -> AccessClaims: ...           # raises typed AuthError on bad/expired
def revoke_refresh(jti: str) -> None: ...
```

### birth_data crypto (`tamthuc_auth/crypto.py`)

```python
def encrypt_birth_data(plaintext: dict, master_key: bytes) -> dict:
    # AES-256-GCM; returns { "alg": "AES-256-GCM", "iv": ..., "ct": ..., "tag": ...,
    #                        "wrapped_dek": ... }  -- the data key is wrapped, never stored bare
def decrypt_birth_data(envelope: dict, master_key: bytes) -> dict: ...
```

### Endpoints (`tamthuc_auth/routes.py`, mounted by FR-API-001)

```
POST /auth/register   { email, password, birth_data? }      -> { user_id, email_verified:false }
POST /auth/login      { email, password }                   -> { access, refresh }
POST /auth/login/google  { id_token }                       -> { access, refresh }   (Authlib OIDC verify)
POST /auth/login/apple   { id_token }                       -> { access, refresh }
POST /auth/refresh    { refresh }                           -> { access, refresh }   (rotates refresh)
GET  /auth/me         (Bearer)                              -> { user_id, email, tier, preferences }
```

### Dependency (`tamthuc_auth/deps.py`)

```python
async def get_current_user(token: str = Depends(bearer)) -> CurrentUser: ...
# verifies the access token, loads the user, exposes id + tier for downstream authorization (FR-AUTH-002)
```

## §4 - Acceptance criteria

1. Register then login with email/password returns an access and a refresh token; the password is stored as an argon2 hash and never appears in the DB or logs in plaintext.
2. `verify_access` accepts a freshly issued token and rejects an expired one, a tampered one, and one signed with the wrong key, each with a typed `AuthError`.
3. `/auth/refresh` issues a new access token and rotates the refresh token; a revoked refresh `jti` is rejected.
4. Google and Apple login verify the provider id token via Authlib OIDC before provisioning; an invalid or wrong-audience id token is rejected, and a first-time social login provisions a user linked by email where one exists.
5. `encrypt_birth_data` / `decrypt_birth_data` round-trip a birth_data dict; the stored envelope contains no plaintext field, the data key is wrapped, and decrypting with the wrong master key fails the GCM tag check rather than returning garbage.
6. Auth failures return the FR-API-001 error envelope with a generic message; login against a non-existent email and login with a wrong password are indistinguishable to the caller (no account enumeration).

## §5 - Verification

- `tests/test_auth.py`: register/login/refresh happy paths; token expiry, tamper, and wrong-key rejection; refresh rotation and revocation; social-login id-token verification with a stubbed OIDC provider (valid, expired, wrong-audience); the account-enumeration-safe failure responses.
- `tests/test_crypto.py`: AES-256-GCM round-trip; wrong-key GCM failure; envelope contains no plaintext; key-rotation path re-wraps the data key without re-encrypting the payload.
- Security checks: passwords never logged (a log-capture assertion); `birth_data` never serialized in plaintext by any response model (`/auth/me` does not return it).
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_auth`, `pytest packages/tamthuc_auth`.

## §6 - Implementation skeleton

1. Create the `tamthuc_auth` package (`pyproject.toml`, `uv`-managed per FR-PLAT-001); this FR owns its birth, FR-AUTH-002/003/004 add modules.
2. `models.py`: `User`, `Profile`, `CurrentUser`; the response models that deliberately exclude `birth_data`.
3. `passwords.py`: argon2 hash/verify via passlib.
4. `tokens.py`: python-jose access/refresh issue + verify + revoke; the `jti` revocation store.
5. `crypto.py`: AES-256-GCM envelope encrypt/decrypt with wrapped data keys; the master-key provider (KMS or config, never the DB).
6. `social.py`: Authlib OIDC clients for Google and Apple; id-token verification and JIT provisioning.
7. `routes.py` + `deps.py` + `config.py`: the endpoints, `get_current_user`, and settings; `migrations/0001_users.sql`.

## §7 - Dependencies

Depends on FR-PLAT-001 (the Python workspace). The `users` table DDL is owned here and applied through the PLAT migration runner into the shared Postgres; the master catalog lists `users` under FR-PLAT-003, so PLAT-003 coordinates the umbrella migration set while AUTH owns the auth columns and the encryption contract - a reconciliation note, with the hard `depends_on` kept at PLAT-001 per the catalog. Blocks FR-AUTH-002 (tiers and quotas key off this user and token), FR-AUTH-003 (email verification / password reset extends this flow), FR-AUTH-004 (DSAR reads and erases this profile), FR-API-001 (`get_current_user` is the gateway's auth dependency), and FR-LEGAL-002 (the PDPD/GDPR pack's retention and erasure contracts operate on this data). TLS in transit and secrets management are enforced by FR-PLAT-007; the audit row for sensitive `birth_data` access is written by FR-API-004.

## §8 - Example payloads

```json
// POST /auth/register
{ "email": "user@example.com", "password": "...", "birth_data":
  { "date": "1990-05-01", "time": "10:30", "place": "Ha Noi", "tz": "+07:00", "kinh_do": 105.85 } }
// -> stored users.birth_data (envelope, illustrative)
{ "alg": "AES-256-GCM", "iv": "b64...", "ct": "b64...", "tag": "b64...", "wrapped_dek": "b64..." }
```

```json
// POST /auth/login -> tokens
{ "access": "eyJ... (15-min JWT, claims sub/tier/iat/exp/jti)", "refresh": "eyJ... (revocable)" }
```

## §9 - Open questions

- Master-key custody: cloud KMS vs an app-held master key in a secret manager. Default: envelope encryption with a wrapped per-record data key so either custody works; the KMS adapter is preferred in production, the secret-manager path is the MVP fallback. Decide with FR-PLAT-007.
- Refresh-token storage: opaque token in a revocation table vs a stateless JWT with a `jti` denylist. Default: `jti`-based revocation with a short denylist window matched to the refresh TTL; revisit if multi-device session management (FR-AUTH-003 scope) needs per-device records.
- Whether Apple's private-relay email counts as a verified email. Default: treat the provider-asserted email as verified for social accounts and skip the email-verification step for them; local email/password accounts still verify. Confirm in FR-AUTH-003.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Plaintext birth_data at rest | encryption skipped or misconfigured | write path refuses to store `birth_data` without a valid envelope; a test asserts no plaintext column |
| Account enumeration | distinct errors for unknown-email vs wrong-password | one generic auth-failure response for both; test asserts indistinguishability |
| Forged social login | client passes an unverified profile | id token verified via Authlib OIDC (issuer, audience, signature, expiry) before any provisioning |
| Token forgery / replay | tampered or expired JWT | `verify_access` rejects with typed `AuthError`; revoked refresh `jti` rejected on rotation |
| Master key in the DB | key stored alongside ciphertext | forbidden by design; the master key comes from KMS/secret manager, never a DB column; code review + config check |
| Password in logs | hash or plaintext logged | passwords and hashes are never logged; a log-capture test asserts absence |

## §11 - Notes

This FR carries the product's highest data-sensitivity obligation, so treat the birth_data encryption and the account-enumeration-safe responses as non-negotiable, not polish. Keep the boundary clean: this FR owns identity, tokens, and the at-rest crypto; FR-AUTH-002 owns what a user is allowed to do and how much; FR-AUTH-004 owns export and erasure; FR-LEGAL-002 owns the consent, retention, and disclosure contracts around all of it. The package `tamthuc_auth` is shared with FR-AUTH-002/003/004; they extend it, so auth is one installable, mypy-clean unit that the FastAPI gateway (FR-API-001) mounts.
