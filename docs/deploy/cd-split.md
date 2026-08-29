# CD split (TASK-PLAT-015 / D-CD-001)

| Surface | Mechanism |
|---|---|
| Web | Vercel Git integration on `main` (+ PR previews) |
| API | `.github/workflows/deploy-vps.yml` → GHCR (digest) → SSH `deploy/vps/deploy.sh` |
| Quality gate | Existing `ci.yml` (must stay green) |
| Image scan CD | `cd.yml` builds images with `push: false` (no registry publish; not the VPS roll path) |

## GitHub secrets (VPS path)

| Secret | Purpose |
|---|---|
| `VPS_HOST` | API host |
| `VPS_USER` | SSH user |
| `VPS_SSH_KEY` | private key |
| `DATABASE_URL` | optional CI migrate dry-run |

`GITHUB_TOKEN` pushes to GHCR.

## Production approval (required — D-CD-001)

The VPS **deploy** job declares `environment: production`. Operators must configure **Required reviewers** on that Environment before treating prod rolls as gated:

1. Settings → Environments → **production** → Required reviewers (named people/teams).
2. Full click-path: `docs/deploy/branch-protection-main.md` § Operator HITL.
3. Also apply branch protection on `main` (`enforce_admins: true`, required checks + PR review).

Until reviewers exist, GitHub may still run the deploy job without a human pause — configuring reviewers is the HITL step agents cannot perform.

## Immutable image pin (D-IMAGE-001 alignment)

- Build tags both `:${{ github.sha }}` and `:main` for convenience.
- SSH deploy sets `API_IMAGE` to **`ghcr.io/<owner>/strategem-api@sha256:…`** (digest from `docker/build-push-action`), never floating `:main`.
- Rollback: set `API_IMAGE` on the VPS `.env` to a prior digest and re-run `deploy/vps/deploy.sh` (see `docs/deploy/vps-api.md`).

## Cutover note

Existing `cd.yml` may still build multi-image Docker CD with `push: false`; treat TASK-PLAT-015 / `deploy-vps.yml` as the **target** path for the Vercel + Supabase + VPS topology. Do not enable unattended prod deploy by removing `environment: production` or Environment reviewers.
