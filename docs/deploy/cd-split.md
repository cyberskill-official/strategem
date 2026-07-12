# CD split (FR-PLAT-015)

| Surface | Mechanism |
|---|---|
| Web | Vercel Git integration on `main` (+ PR previews) |
| API | `.github/workflows/deploy-vps.yml` → GHCR → SSH `deploy/vps/deploy.sh` |
| Quality gate | Existing `ci.yml` (must stay green) |

## GitHub secrets (VPS path)

| Secret | Purpose |
|---|---|
| `VPS_HOST` | API host |
| `VPS_USER` | SSH user |
| `VPS_SSH_KEY` | private key |
| `DATABASE_URL` | optional CI migrate dry-run |

`GITHUB_TOKEN` pushes to GHCR.

## Production approval

Optional: GitHub Environment `production` required reviewers before VPS job (same spirit as FR-PLAT-004).

## Cutover note

Existing `cd.yml` may still build multi-image Docker CD; treat FR-PLAT-015 as the **target** path for the Vercel + Supabase + VPS topology. Disable conflicting web-in-Docker prod deploys when Vercel is primary.
