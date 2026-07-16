# Production environment (TASK-PLAT-004)

| Item | Value |
|---|---|
| Purpose | User-facing release |
| Image tags | same `${git SHA}` promoted from staging |
| Approval | **required** — GitHub Environment `production` with required reviewers |
| Secrets | production secret store / environment only |

## Promote

1. Staging auto-deploys on merge.
2. Human approves the `deploy-prod` job (Environment protection).
3. Same SHA rolls to production; tag recorded.

## Rollback

Re-run promote for a prior SHA that was recorded as good; production must never deploy unapproved SHAs.
