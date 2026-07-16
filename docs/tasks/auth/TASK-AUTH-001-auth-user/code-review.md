---
artefact: code-review@1
fr_id: TASK-AUTH-001
status: ready_for_human_acceptance
reviewed_at: 2026-07-13
verdict_pending: human reviewing → ready_to_test
---

# Code review — TASK-AUTH-001

## Delivered

| Path | Role |
|---|---|
| `packages/tamthuc_auth/` | Full auth package (models, passwords, tokens, crypto, social, routes, deps, service, store) |
| `packages/tamthuc_auth/migrations/0001_users.sql` | AUTH column additions (email_verified, birth_data jsonb, social) |
| `docs/contracts/auth-tokens.md` | JWT claim contract |
| `packages/tamthuc_auth/tests/` | AC coverage |

## §4 AC → tests

| AC | Test | Status |
|---|---|---|
| 1 register/login + argon2 | `test_register_login_tokens`, `test_password_argon2_*` | pass |
| 2 verify_access reject expired/tampered/wrong-key | `test_verify_access_rejects_*` | pass |
| 3 refresh rotates; revoked jti rejected | `test_refresh_rotation_and_revocation` | pass |
| 4 Google/Apple id_token verify + JIT | `test_social_google_and_apple`, invalid/aud/exp | pass |
| 5 AES-GCM round-trip, no plaintext, wrong key | `test_crypto.py` | pass |
| 6 generic auth failure (no enum) | `test_login_failures_indistinguishable`, HTTP | pass |

## Gate evidence

```
uv run pytest -q packages/tamthuc_auth --cov=tamthuc_auth
23 passed; TOTAL 96%; every module file ≥ 92%
mypy packages/tamthuc_auth — clean
full python lane — 44 passed, 6 skipped
```

## Notes

- Persistence is protocol + `InMemoryUserStore` for unit tests; production Postgres wiring is TASK-API-004. DDL lives under AUTH migrations + PLAT-003 coordination.
- Social OIDC uses JWT audience/issuer verify (Authlib-shaped); production JWKS adapter is TASK-PLAT-007 / follow-on.
- `/auth/me` never returns `birth_data`.

## Recommendation

**Approve** review acceptance: `APPROVE review TASK-AUTH-001`
