---
artefact: coverage-gate@1
fr_id: FR-AUTH-001
outcome: PASS
tests_failed: 0
review_approved: "APPROVE review FR-AUTH-001 (operator chat)"
---

# Coverage gate — FR-AUTH-001

## Command

```
uv run pytest -q packages/tamthuc_auth --cov=tamthuc_auth --cov-report=term-missing
```

## Result

```
23 passed
TOTAL 96%
per-file: all ≥ 92% (deps 100%, passwords 100%, models 100%, tokens 92%, …)
ruff + mypy: clean
```

## TRACE-004

| §4 AC | Named test | Status |
|---|---|---|
| 1 register/login argon2 | `test_register_login_tokens`, `test_password_argon2_not_plaintext` | **passed** |
| 2 token reject paths | `test_verify_access_rejects_expired_tampered_wrong_key` | **passed** |
| 3 refresh rotate/revoke | `test_refresh_rotation_and_revocation` | **passed** |
| 4 social OIDC | `test_social_google_and_apple`, `test_social_invalid_and_wrong_audience` | **passed** |
| 5 birth_data crypto | `tests/test_crypto.py` | **passed** |
| 6 no account enumeration | `test_login_failures_indistinguishable` | **passed** |

## Module gates

- awh: N/A
- caf: N/A

## files_below_90pct

(empty)
