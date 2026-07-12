# Consent capture (signup)

Consent is **granular**, **revocable**, **versioned**, and **timestamped** at signup:

| Field | Required |
|---|---|
| `consent_version` | policy document version string |
| `purposes[]` | e.g. `chart_cast`, `ai_interpretation`, `marketing` |
| `granted_at` | RFC3339 timestamp |
| `subject_id` | user id |
| `revoked_at` | null until withdrawal |

FR-AUTH-001 registration emits verification; FR-AUTH-003 completes email verify; consent rows are stored with the user profile (implementation FR-AUTH-004/API-004).
