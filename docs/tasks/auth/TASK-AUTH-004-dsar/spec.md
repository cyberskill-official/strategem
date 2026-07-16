---
id: TASK-AUTH-004
title: "DSAR self-service - data-subject access request export (a machine-readable copy of all personal data) and right-to-erasure over the AUTH-001 profile and the persisted history, honoring the LEGAL-002 PDPD/GDPR retention and disclosure contracts; erasure crypto-shreds birth_data and is audited"
module: AUTH
priority: SHOULD
status: done
phase: P2
slice: 1
lang: python
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Grok-36, strategy 4.4, strategy 7, strategy RISK-5]
related_frs: [TASK-AUTH-001, TASK-API-004, TASK-PLAT-003, TASK-PLAT-009, TASK-LEGAL-002]
depends_on: [TASK-AUTH-001, TASK-LEGAL-002]
blocks: []
new_paths:
  - packages/tamthuc_auth/tamthuc_auth/dsar.py
  - packages/tamthuc_auth/tamthuc_auth/export.py
  - packages/tamthuc_auth/tamthuc_auth/erasure.py
  - packages/tamthuc_auth/tests/test_export.py
  - packages/tamthuc_auth/tests/test_erasure.py
  - docs/contracts/dsar.md
---

## §1 - Description (BCP-14 normative)

This task is the data-subject self-service for privacy rights: export (a machine-readable copy of everything the platform holds about a user) and erasure (right to be forgotten). It extends the `tamthuc_auth` package and executes the DSAR obligations TASK-LEGAL-002 defines. It owns the export and erasure operations over the user's data; it does NOT own the legal policy - the retention windows, the lawful bases, the disclosure text - which belong to TASK-LEGAL-002; this task is the mechanism that enforces that policy on the actual tables.

Export SHALL assemble a complete, machine-readable copy of the user's personal data across the TASK-PLAT-003 tables - the profile (TASK-AUTH-001, with `birth_data` decrypted for the subject's own export), queries, charts, reports, and the relevant audit trail - and SHALL return it as a structured archive (JSON), scoped strictly to the requesting user under row-level security so no other user's data can leak into an export. Erasure SHALL remove or irreversibly de-identify the user's personal data: it SHALL soft-delete the profile (`users.deleted_at`, TASK-PLAT-003) and crypto-shred `birth_data` by destroying the wrapped per-record data key (TASK-AUTH-001 envelope encryption), so the ciphertext - including copies in backups (TASK-PLAT-009) - becomes permanently unreadable without a per-row rewrite. Erasure SHALL honor the TASK-LEGAL-002 retention contract: records under a legal retention obligation (for example audit rows required for a defined period) SHALL be retained per policy rather than deleted, and the response SHALL state what was erased and what was retained and why.

Both operations SHALL require a freshly authenticated principal (re-authentication or a recent session) because they are high-impact, SHALL be audited via TASK-API-004 (`dsar_export`, `dsar_erase`) without copying the exported sensitive payload into the audit row, and SHALL be idempotent and safe to retry. Export SHALL be delivered so the archive itself is protected (authenticated, time-limited access), not left at a public URL. Failures SHALL return the TASK-API-001 error envelope.

## §2 - Why this design (rationale for humans)

Export and erasure are legal rights under VN PDPD and GDPR, and the product's whole positioning rests on honoring them credibly (strategy 7, RISK-5). The hard part of export is completeness and scoping at once: it must gather everything about the user across every table, and it must gather nothing about anyone else. Running the export under the same fail-closed RLS the rest of the platform uses (TASK-PLAT-003) is what makes the second guarantee structural rather than a careful join - a bug in the export query cannot pull another user's rows because the database refuses them. Decrypting `birth_data` for the subject's own export is correct (it is their data) but the archive is then sensitive, so it is delivered under authenticated, time-limited access rather than a public link.

Erasure is where the encryption design pays off. Hard-deleting rows across a live database, its replicas, and its backups is slow, error-prone, and often incompatible with legal retention of some records. Crypto-shredding - destroying the wrapped per-record key so the AES-256 ciphertext can never be decrypted again - erases the birth data everywhere it exists, including in backups (TASK-PLAT-009), in a single stroke, because ciphertext without its key is noise. That is exactly why TASK-AUTH-001 wrapped a per-record data key in the first place. Pairing crypto-shred with a soft-delete of the profile and an explicit honoring of the retention contract (some audit records must survive for a legally defined period) gives an erasure that is both complete for the sensitive payload and lawful about what it keeps - and the response says so, rather than pretending everything vanished. Requiring fresh authentication and auditing the action (without copying the payload) keeps a destructive, irreversible operation from being trivially triggerable and keeps a record that it happened.

## §3 - Contract (export / erasure / audit)

### Export (`export.py`)

```python
async def export_user_data(user_id: str) -> DsarArchive:
    # gather, under RLS scoped to user_id:
    #   profile (birth_data DECRYPTED for the subject), queries, charts, reports, relevant audit rows
    # -> a structured JSON archive; delivered via authenticated, time-limited access (never a public URL)
```

### Erasure (`erasure.py`)

```python
async def erase_user_data(user_id: str) -> ErasureResult:
    # 1. crypto-shred birth_data: destroy the wrapped per-record data key (TASK-AUTH-001) -> ciphertext unreadable
    # 2. soft-delete the profile (users.deleted_at, TASK-PLAT-003)
    # 3. de-identify / delete queries+charts+reports per the TASK-LEGAL-002 retention contract
    # 4. RETAIN records under legal retention (e.g. required audit rows); report what was kept and why
    # -> ErasureResult { erased: [...], retained: [{ table, reason }], crypto_shredded: true }
```

### Endpoints (mounted by TASK-API-001; require fresh authentication)

```
POST /auth/me/export   (Bearer, re-auth)  -> { archive_ref }   # authenticated, time-limited download
POST /auth/me/erase    (Bearer, re-auth)  -> ErasureResult      # crypto-shred + soft-delete + retention report
```

### Audit (via TASK-API-004)

`dsar_export` and `dsar_erase` audit rows record that the action occurred, by whom, and the scope - never the exported sensitive payload.

## §4 - Acceptance criteria

1. Export returns a machine-readable archive containing the user's profile (with `birth_data` decrypted for the subject), queries, charts, reports, and relevant audit rows, and contains no other user's data (RLS-scoped); a cross-user leakage test finds nothing foreign.
2. The export archive is delivered under authenticated, time-limited access, not a public URL; an unauthenticated or expired access attempt is refused.
3. Erasure crypto-shreds `birth_data` (the wrapped data key is destroyed) so the ciphertext can no longer be decrypted - verified by attempting decryption post-erasure and getting failure, not plaintext - and this holds for backup copies by construction (no key, no plaintext).
4. Erasure soft-deletes the profile and de-identifies/deletes the user's history per the TASK-LEGAL-002 retention contract, while retaining records under a legal retention obligation; the result reports what was erased and what was retained and why.
5. Both operations require a freshly authenticated principal and are audited via TASK-API-004 (`dsar_export`/`dsar_erase`) with no sensitive payload copied into the audit row; both are idempotent on retry.
6. All failures return the TASK-API-001 error envelope; an erased user can no longer authenticate and their `birth_data` is unrecoverable.

## §5 - Verification

- `tests/test_export.py`: completeness (all of the subject's tables represented); RLS scoping (no foreign rows, driven with two users); the decrypted-birth_data-for-subject case; authenticated/time-limited delivery (expired access refused).
- `tests/test_erasure.py`: crypto-shred (post-erasure decryption fails, not returns plaintext); soft-delete of the profile; retention honored (a required audit row survives; the result lists it with a reason); idempotent retry; erased user cannot authenticate.
- Security checks: the audit rows for export/erase carry no exported payload; a fresh-auth requirement is enforced (a stale session is rejected).
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_auth`, `pytest packages/tamthuc_auth`.

## §6 - Implementation skeleton

1. `export.py`: gather the subject's data across the TASK-PLAT-003 tables under RLS; decrypt `birth_data` for the subject; assemble the JSON archive.
2. `erasure.py`: crypto-shred (destroy the wrapped DEK), soft-delete the profile, de-identify/delete history per TASK-LEGAL-002 retention, retain legally required records and report them.
3. `dsar.py`: the orchestration + the fresh-auth requirement + the authenticated, time-limited archive delivery.
4. Wire the two endpoints into the TASK-API-001 router; emit `dsar_export`/`dsar_erase` audit rows via TASK-API-004 (no payload); render errors in the TASK-API-001 envelope.
5. Align the retention rules and the disclosure text with TASK-LEGAL-002; document the DSAR contract in `docs/contracts/dsar.md`.

## §7 - Dependencies

Depends on TASK-AUTH-001 (the profile it exports/erases and, critically, the envelope encryption whose wrapped per-record key makes crypto-shred possible) and TASK-LEGAL-002 (the retention windows, lawful bases, and disclosure text this task enforces mechanically). Operates over the TASK-PLAT-003 tables and relies on their fail-closed RLS to scope an export; erasure's crypto-shred reaches backup copies governed by TASK-PLAT-009. Audited via TASK-API-004 (`dsar_export`/`dsar_erase`); endpoints mounted by and errors rendered through TASK-API-001. This is the AUTH mechanism behind the LEGAL-002 privacy contracts and completes the RISK-5 posture (export + erasure).

## §8 - Example payloads

```json
// POST /auth/me/erase -> ErasureResult (reports erased vs legally retained)
{ "crypto_shredded": true,
  "erased": ["users.birth_data", "users.profile", "queries", "charts", "reports"],
  "retained": [ { "table": "audit_logs", "reason": "legal retention window (TASK-LEGAL-002)", "until": "2029-07-08" } ] }
```

```json
// dsar_erase audit row (via TASK-API-004) - records the fact + scope, never the payload
{ "action": "dsar_erase", "user_id": "u_...",
  "details": { "crypto_shredded": true, "retained_tables": ["audit_logs"] }, "created_at": "..." }
```

## §9 - Open questions

- Erasure of `queries`/`charts`/`reports`: hard-delete vs de-identify. Default: crypto-shred the sensitive `birth_data`, then hard-delete or de-identify the query/chart/report rows per the TASK-LEGAL-002 retention contract (charts derived from erased birth data have limited standalone value); the exact treatment is a LEGAL-002 decision this task enforces.
- Export format and portability. Default: a structured JSON archive at MVP (machine-readable, GDPR-portable); a human-readable rendering or an additional format is additive and does not change the gather/scope logic.
- Delivery mechanism for the archive. Default: an authenticated, time-limited download reference (not a public URL); an emailed link must itself be single-use and expiring (reuse the TASK-AUTH-003 token discipline).

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Cross-user export leak | export pulls another user's rows | forbidden; export runs under fail-closed RLS scoped to the subject; a leakage test finds nothing foreign |
| Recoverable birth_data after erasure | ciphertext still decryptable | forbidden; crypto-shred destroys the wrapped key; post-erasure decryption fails, including in backups |
| Retention violated | a legally required record deleted | records under a retention obligation are retained per TASK-LEGAL-002; the result reports what was kept and why |
| Sensitive payload in audit | exported data copied into the audit row | forbidden; the audit row records the fact + scope, never the payload |
| Trivially triggerable erasure | destructive op without fresh auth | export/erase require a freshly authenticated principal |
| Archive left public | export archive at an open URL | delivered under authenticated, time-limited access only |

## §11 - Notes

This task turns the AUTH-001 encryption design and the LEGAL-002 policy into working privacy rights: export gathers everything about the subject (and nothing about anyone else, guaranteed by fail-closed RLS), and erasure crypto-shreds `birth_data` by destroying its wrapped key so the ciphertext dies everywhere at once, backups included, while honoring the legal retention the LEGAL-002 contract requires and reporting exactly what was kept. Keep the boundary clean: LEGAL-002 owns the policy (windows, bases, disclosure), this task owns the mechanism (export, crypto-shred, soft-delete, retention enforcement). It extends `tamthuc_auth`, requires fresh authentication for both destructive/high-impact operations, and audits them through TASK-API-004 without copying the payload. Together with TASK-AUTH-001 it completes the RISK-5 posture.
