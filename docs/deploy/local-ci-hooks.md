# Local CI + hooks (before GitHub)

Status page, lint, build, and tests must pass **on the machine** before code hits GitHub. CyberOS + this repo wire that as follows.

## Do not remove

| Piece | Role |
|-------|------|
| `.cyberos/migrate-frs.sh` | **`migrate-frs --page`** regenerates `docs/status/` from FR frontmatter. Permanent. |
| `docs/status/` | Tracked HTML board — what GitHub Pages / operators open |
| `scripts/check-status-sync.sh` | CI + local: fail if board counts lag frontmatter |
| `scripts/local-ci.sh` | One-shot local CI floor |
| `scripts/git-hooks/*` | Source of truth for install into `.git/hooks/` |

## Install (once per clone)

```bash
cp scripts/git-hooks/pre-commit .git/hooks/pre-commit
cp scripts/git-hooks/pre-push  .git/hooks/pre-push
chmod +x .git/hooks/pre-commit .git/hooks/pre-push scripts/local-ci.sh scripts/check-status-sync.sh
```

CyberOS `init` also installs a **status-hook v2** into pre-commit (blocking regen). This repo’s combined hook already includes that behavior.

## What runs when

| Event | Status page | Version | Lint | Build / compose | Tests | act |
|-------|-------------|---------|------|-----------------|-------|-----|
| **pre-commit** (FR/CHANGELOG/VERSION staged) | regen + stage + check | VERSION↔package.json if VERSION staged | staged py/web/rust | — | — | — |
| **pre-push** | check (+ regen if FR lane) | package.json info + VERSION match | lanes | cargo + compose config | pytest/cargo/web | optional FULL |
| **GitHub CI** | `status-sync` job | — | full | full | full | n/a |

## Manual commands

```bash
# Status only
bash .cyberos/migrate-frs.sh --page .
bash scripts/check-status-sync.sh

# Local CI floor (same as pre-push default)
bash scripts/local-ci.sh

# Fast (lint + status)
LOCAL_CI_QUICK=1 bash scripts/local-ci.sh

# + act status-sync job
LOCAL_CI_FULL=1 bash scripts/local-ci.sh

# Full ci.yml under act (heavy)
LOCAL_CI_FULL=1 LOCAL_CI_ACT_ALL=1 bash scripts/local-ci.sh
# only: act push -W .github/workflows/ci.yml --container-architecture linux/amd64
```

## Version / build-number

| File | Meaning |
|------|---------|
| `package.json` `version` | **Product** version (Strategem) |
| `.cyberos/VERSION` | **CyberOS payload** version (platform), not product |
| `VERSION` (if present at repo root) | Must match `package.json` when both exist |
| `BUILD_NUMBER` (if present) | Informational build stamp |

CyberOS platform repos additionally run `check-version-sync.sh` on payload stamps — that is for **cyberos** itself, not every consumer.

## Compose (local)

```bash
docker compose -f deploy/compose/docker-compose.local.yml config --quiet
# full stack
export LOCAL_API_PORT=18000 LOCAL_WEB_PORT=13000 API_URL=http://api:8000
export NEXT_PUBLIC_API_BASE=http://127.0.0.1:18000
docker compose -f deploy/compose/docker-compose.local.yml up --build -d
```

`local-ci.sh` validates compose **config** on pre-push (not a full image build unless you opt in).

## act notes

- Pin workflow: `-W .github/workflows/ci.yml` (other workflows may fail act schema, e.g. deploy secrets).
- Apple Silicon: `--container-architecture linux/amd64` if images fail.
- Default pre-push sets `SKIP_ACT=1`; use `LOCAL_CI_FULL=1` to exercise act.
