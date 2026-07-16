# PDPD / GDPR compliance pack (TASK-LEGAL-002)

## Legal basis

- Vietnam: **Nghị định 13/2023/NĐ-CP** (PDPD)
- EU: **GDPR** (Regulation (EU) 2016/679)
- Rule: meet the **stricter** requirement per control.

## Data classification

Birth data and question text are **sensitive personal data**. Charts/reports are personal. Audit is operational and **erasure-exempt** (fact of erasure retained).

## Logging rule

No plaintext `birth_data` or full question text in logs, metrics labels, Sentry, or analytics (aligns with TASK-PLAT-005 redaction).

## Modules

| Artefact | Role |
|---|---|
| `retention-schedule.md` + `retention.py` | per-class retention |
| `consent.md` | granular signup consent |
| `docs/contracts/dsar.schema.json` | export/erasure shapes for TASK-AUTH-004 |
| `tamthuc_compliance` | typed contracts + stub |
