# OWASP Top 10 checklist (release gate)

| Item | Status | Notes |
|---|---|---|
| A01 Broken Access Control | addressed | RBAC deps AUTH-002 |
| A02 Cryptographic Failures | addressed | TLS 1.3, AES-GCM birth_data |
| A03 Injection | addressed | input validation |
| A04 Insecure Design | addressed | STRIDE model |
| A05 Security Misconfiguration | addressed | security headers |
| A06 Vulnerable Components | addressed | Trivy/Dependabot workflows |
| A07 Auth Failures | addressed | argon2, generic errors |
| A08 Software/Data Integrity | addressed | signed envelopes |
| A09 Logging/Monitoring | addressed | PLAT-005, no PII in logs |
| A10 SSRF | deferred | no user-controlled SSRF sinks in P0 |
