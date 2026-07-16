---
artefact: edge-case-matrix@1
fr_id: TASK-AUTH-001
---

# Edge-case matrix — TASK-AUTH-001

| id | category | case | expected | coverage |
|---|---|---|---|---|
| EC-1 | null/empty | empty password hash path | ValueError / failed verify | `test_password_empty_raises` |
| EC-2 | bounds | expired JWT | TokenExpired | `test_verify_access_rejects_*` |
| EC-3 | malformed | tampered JWT | TokenInvalid | same |
| EC-4 | security | wrong JWT secret | TokenInvalid | same |
| EC-5 | security | account enumeration | identical failure envelopes | `test_login_failures_indistinguishable` |
| EC-6 | security | plaintext birth_data at rest | envelope only | `test_envelope_has_no_plaintext` + register |
| EC-7 | security | wrong master key decrypt | GCM InvalidTag | `test_wrong_master_key_fails_gcm` |
| EC-8 | security | password never logged | log capture | `test_passwords_never_logged` |
| EC-9 | security | forged social token | SocialTokenInvalid | `test_social_invalid_*` |
| EC-10 | concurrent | refresh rotation | old jti revoked | `test_refresh_rotation_and_revocation` |

`total_rows: 10`
