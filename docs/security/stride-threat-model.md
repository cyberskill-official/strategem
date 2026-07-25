# STRIDE threat model (TASK-PLAT-007)

| Threat | Control | Evidence |
|---|---|---|
| Spoofing | JWT + API keys (AUTH-001/002) | token verify tests |
| Tampering | HMAC chart signing | `test_signed_envelope_tamper_detected` |
| Repudiation | audit_logs (PLAT-003) | schema + RLS |
| Information disclosure | AES-256 birth_data, TLS 1.3, redaction | AUTH-001 crypto, headers, PLAT-005 redact |
| Denial of service | rate limits (AUTH-002 quotas / API-003); WAF **planned** (not deployed) | rbac-tiers; `waf-rules.md` (sketch) |
| Elevation of privilege | RBAC require_* | AUTH-002 scopes tests |

Every row has evidence; empty evidence fails review.
