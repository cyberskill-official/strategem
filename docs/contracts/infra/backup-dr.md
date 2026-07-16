# Backup + DR (TASK-PLAT-009)

| Objective | Target |
|---|---|
| RPO | 1 hour (PITR continuous WAL / continuous backup) |
| RTO | 4 hours |
| Primary store | Postgres (TASK-PLAT-003) with point-in-time recovery |
| Drill | Quarterly restore drill; evidence logged |

## Procedure (summary)

1. **Backup:** continuous WAL archiving + daily base backup; retention per LEGAL-002.
2. **Restore:** restore base + replay WAL to target timestamp (RPO ≤ 1h).
3. **Crypto-shred compatibility:** AUTH-004 birth_data crypto-shred remains effective in backups (ciphertext without DEK).
4. **Drill:** run `scripts/dr-drill.md` checklist; record start/end, measured RTO.

## Acceptance

- Documented RPO 1h / RTO 4h
- PITR path documented
- Drill cadence quarterly
