---
id: FR-PLAT-015
title: "CD split - GitHub Actions builds/pushes API (+ engine) images to GHCR and SSH-rolls VPS; Vercel deploys web from main; production still behind human approval for VPS prod env"
module: PLAT
priority: MUST
status: done
phase: P3
slice: 1
lang: iac
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-13
refs: [cyberos .github/workflows/deploy.yml, FR-PLAT-004]
related_frs: [FR-PLAT-004, FR-PLAT-011, FR-PLAT-013, FR-PLAT-014]
depends_on: [FR-PLAT-013, FR-PLAT-014]
blocks: []
new_paths:
  - .github/workflows/deploy-vps.yml
  - docs/deploy/cd-split.md
---

## §1 - Description (BCP-14 normative)

This FR splits continuous delivery by surface (CyberOS auto-deploy pattern + operator topology):

| Trigger | Web (Vercel) | API/engine (VPS) |
|---|---|---|
| push `main` | Vercel Git integration deploys `apps/web` | Actions: build image → GHCR → SSH `deploy.sh` |
| PR | Vercel preview (optional) | CI only (no VPS roll) |

Production VPS roll MAY stay behind GitHub Environment `production` approval (FR-PLAT-004 human gate). Staging VPS can auto-roll.

Secrets: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`, registry via `GITHUB_TOKEN`. No Vercel token required if Git integration is linked.

## §2 - Why this design

One monorepo, two deploy machines: Vercel owns edge web; VPS owns stateful API. CI stays the quality gate; CD is promotion only.

## §3 - Contract

Workflow `deploy-vps.yml`:

1. checkout + build `deploy/docker/api.Dockerfile` (+ engine if needed)
2. push `ghcr.io/<owner>/strategem-api:<sha>` and `:main`
3. SSH: run `deploy/vps/deploy.sh` with env tag

Document Vercel project settings separately (FR-PLAT-014).

## §4 - Acceptance criteria

1. Workflow file exists and is `workflow_dispatch` + `push` to main capable.
2. Docs list required GitHub secrets.
3. Does not break existing `ci.yml` / `cd.yml` until cutover is documented.

## §5 - Verification

- YAML validates; dry-run instructions in docs.
