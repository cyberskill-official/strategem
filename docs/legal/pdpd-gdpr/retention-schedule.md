# Retention schedule

| Class | Sensitivity | Retention | Erasure |
|---|---|---|---|
| birth_data | sensitive | account life + 30d | crypto-shred |
| question_text | sensitive | account life + 30d | crypto-shred |
| charts | personal | account life | soft-delete |
| reports | personal | account life | soft-delete |
| audit | operational | 7 years | retain |

See `tamthuc_compliance.retention.DATA_CLASSES` for machine-readable form.
