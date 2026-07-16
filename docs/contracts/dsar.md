# DSAR self-service (TASK-AUTH-004)

Implements the export / erasure mechanisms required by TASK-LEGAL-002 (PDPD / GDPR).

## Export

- Machine-readable JSON archive of the subject's profile (birth_data **decrypted for the subject**), queries, charts, reports, and relevant audit rows.
- Scoped by user id (RLS / application filter); no foreign rows.
- Delivered via authenticated, **time-limited** `archive_ref` + token — never a public URL.

## Erasure

1. **Crypto-shred** `birth_data`: destroy the wrapped per-record DEK so AES-256 ciphertext is permanently unreadable (including backups by construction).
2. **Soft-delete** profile (`deleted_at` / preferences marker).
3. De-identify / delete history tables per retention policy.
4. **Retain** legally required audit rows; report them with reasons.

## Endpoints

```
POST /auth/me/export   (fresh auth) → { archive_ref, token, expires_at }
POST /auth/me/erase    (fresh auth) → ErasureResult
```

Audit actions `dsar_export` / `dsar_erase` never copy the exported sensitive payload.
