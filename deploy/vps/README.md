# VPS API deploy (FR-PLAT-013)

See `docs/deploy/vps-api.md` and `docs/deploy/topology.md`.

```bash
cp .env.example .env   # edit secrets
chmod +x migrate.sh deploy.sh
bash migrate.sh
bash deploy.sh
```
