---
artefact: coverage-gate@1
fr_id: FR-AUTH-002
outcome: PASS
tests_failed: 0
review_approved: "APPROVE all (operator)"
---
# Coverage gate — FR-AUTH-002
- pytest packages/tamthuc_auth: 33 passed
- total coverage 95%; scopes.py 94%; all modules ≥92%
- TRACE: roles closed, config parity, capability deny free/allow premium, quotas, API key hash/revoke, tier order
- awh/caf: N/A
