# AUTH - auth and user management

The identity and authorization layer: registration and login (email/password plus Google and Apple social login), JWT access and refresh tokens, the user profile that holds sensitive birth_data, the RBAC tiers that are both the plan ladder and the primary cost control, and the privacy self-service (email verification, password reset, DSAR export and erasure). Language is Python (DEC-2); everything lives in one package, `tamthuc_auth`, mounted by the FastAPI gateway (TASK-API-001). Primary sources: Grok 36 (auth, tiers, social login, backend spec), Claude 07 (tier positioning). See the unified plan sections 4.4, 7, and RISK-5.

## tasks

| task | Pri | Phase | h | Title |
|---|---|---|--:|---|
| AUTH-001 | MUST | P0 | 14 | [Auth (JWT + refresh, email + Google/Apple) + birth-data AES-256 + profile](TASK-AUTH-001-auth-user/spec.md) |
| AUTH-002 | MUST | P0 | 8 | [RBAC tiers (Free/Premium/Enterprise/Admin) + rate-limit tiers](TASK-AUTH-002-rbac-tiers/spec.md) |
| AUTH-003 | SHOULD | P1 | 6 | Email verification + password reset |
| AUTH-004 | SHOULD | P2 | 8 | DSAR self-service (export + erasure) |

Two P0 tasks are authored (AUTH-001 identity + crypto, AUTH-002 tiers + quotas). Two are authored: AUTH-003 (email verification and password reset, P1) and AUTH-004 (DSAR self-service export and erasure, P2, gated on TASK-LEGAL-002).

## Internal spine

```
AUTH-001 (users + JWT/refresh + email/Google/Apple + birth_data AES-256-GCM + profile)
   -> AUTH-002 (RBAC Free/Premium/Enterprise/Admin + per-tier quota config; Enterprise API key)
   -> AUTH-003 (email verification + password reset; P1)
   -> AUTH-004 (DSAR export + erasure; P2)  [needs LEGAL-002]
```

## Cross-module dependencies

- Depends on PLAT-001 (the Python workspace). The `users` table DDL is owned in AUTH-001 and run through the PLAT migration runner into the shared Postgres; the master catalog lists `users` under PLAT-003, which coordinates the umbrella migration set (a reconciliation note, hard `depends_on` kept at PLAT-001).
- Blocks API: TASK-API-001 uses `get_current_user` as its auth dependency and mounts the `/auth/*` routes; TASK-API-003 reads AUTH-002's `quota_for` and the `rbac-tiers.json` single-source config to enforce per-tier limits; TASK-API-004 writes audit rows for the auth and tier-change events raised here.
- Blocks LEGAL: TASK-LEGAL-002 (the PDPD/GDPR pack) operates its consent, retention, and disclosure contracts on the AUTH-001 profile, and TASK-AUTH-004 executes DSAR against the persisted user data. TASK-PLAT-007 enforces TLS in transit and secrets/KMS custody for the birth_data master key.
- Consumed by WEB: the login, profile, and school-flag-default surfaces (TASK-WEB-001/002/007) sign in and read preferences through these endpoints.

## Module notes

- Sensitive personal data is the defining constraint. birth_data (date, time, place) and question text are sensitive personal data. The posture is non-negotiable: AES-256-GCM encryption at rest with a master key held outside the database (envelope encryption, wrapped per-record data key), TLS in transit (enforced at the platform edge, TASK-PLAT-007), an append-only audit row on every sensitive read or write (TASK-API-004), and PDPD plus GDPR erasure and export honored (TASK-AUTH-004, TASK-LEGAL-002). This is the AUTH expression of RISK-5, and the platform's legal footing (strategy 7) rests on it.
- Auth failures do not leak account existence. Unknown-email and wrong-password login failures are indistinguishable to the caller; social login verifies the provider OIDC id token before provisioning, never trusting a client-passed profile.
- Tiers are the plan ladder and the cost control, from one config. Free / Premium / Enterprise / Admin and their quotas (Free 100/day, Premium 5000/day, Enterprise custom, Admin unmetered) live in one machine-readable artifact that both AUTH-002 and TASK-API-003 read, so the advertised limit and the enforced limit are the same number in one place. Capability (what you may do) is kept separate from quota (how much); Enterprise adds machine-to-machine API-key auth.
- One package, one installable unit. All four tasks extend `tamthuc_auth` (tokens, crypto, social, rbac, tiers, apikey, dsar modules), so auth is one mypy-clean, pytest-covered Python package the gateway mounts.
