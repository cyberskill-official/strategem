# Staging environment (TASK-PLAT-004)

| Item | Value |
|---|---|
| Purpose | Auto-deploy on merge to `main` |
| Image tags | `${git SHA}` + moving `staging` |
| Compose | `deploy/compose/docker-compose.staging.yml` |
| Secrets | CI secret store only (never repo) — JWT secret, DB password, registry creds |
| Approval | none (automatic) |

## Rollback

```bash
# re-deploy prior known-good SHA
export IMAGE_TAG=<previous-sha>
docker compose -f deploy/compose/docker-compose.staging.yml up -d
echo "$IMAGE_TAG" > deploy/records/staging.tag
```
