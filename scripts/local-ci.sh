#!/usr/bin/env bash
# Local pre-GitHub CI for Strategem (and CyberOS consumer pattern).
#
# Runs (unless skipped via env):
#   1) status page sync check (+ optional regen)
#   2) version consistency (product package.json ↔ any VERSION stamp we track)
#   3) lint (ruff / cargo fmt+clippy / web eslint) for changed lanes
#   4) build (cargo, web next build optional, docker compose config)
#   5) tests (pytest / cargo test / web test — scoped)
#   6) optional: act -W .github/workflows/ci.yml
#
# Env skips (for speed):
#   SKIP_STATUS=1 SKIP_VERSION=1 SKIP_LINT=1 SKIP_BUILD=1 SKIP_TEST=1 SKIP_COMPOSE=1 SKIP_ACT=1
#   LOCAL_CI_QUICK=1  → lint+status only (no build/test/act)
#   LOCAL_CI_FULL=1   → everything including act
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

if [ "${LOCAL_CI_QUICK:-0}" = "1" ]; then
  SKIP_BUILD="${SKIP_BUILD:-1}"
  SKIP_TEST="${SKIP_TEST:-1}"
  SKIP_ACT="${SKIP_ACT:-1}"
  SKIP_COMPOSE="${SKIP_COMPOSE:-1}"
fi

# Detect lanes from git (diff vs origin/main or HEAD~1)
base_ref="${LOCAL_CI_BASE:-origin/main}"
if git rev-parse --verify "$base_ref" >/dev/null 2>&1; then
  changed="$(git diff --name-only "$base_ref"...HEAD 2>/dev/null || git diff --name-only HEAD)"
else
  changed="$(git diff --name-only HEAD 2>/dev/null || true)"
fi
# Also include unstaged/staged for pre-push of dirty tree
changed="$(printf '%s\n%s\n' "$changed" "$(git diff --name-only; git diff --cached --name-only)" | sort -u)"

has() { grep -Eq "$1" <<<"$changed"; }

lane_py=0; lane_rs=0; lane_web=0; lane_fr=0; lane_compose=0
if has '\.py$' || has '^packages/' || has 'pyproject'; then lane_py=1; fi
if has '\.rs$' || has '^crates/' || has 'Cargo'; then lane_rs=1; fi
if has '^apps/web/' || has 'pnpm-lock'; then lane_web=1; fi
if has '^docs/feature-requests/' || has 'CHANGELOG' || has '^VERSION$'; then lane_fr=1; fi
if has 'docker-compose|Dockerfile'; then lane_compose=1; fi

# If nothing detected (first run / empty), assume all product lanes
if [ "$lane_py$lane_rs$lane_web" = "000" ]; then
  lane_py=1; lane_rs=1; lane_web=1
fi

echo "local-ci: lanes py=$lane_py rs=$lane_rs web=$lane_web fr=$lane_fr compose=$lane_compose"

# ── 1) Status page ──────────────────────────────────────────────────────────
if [ "${SKIP_STATUS:-0}" != "1" ]; then
  if [ "$lane_fr" = "1" ] || [ -n "${FORCE_STATUS:-}" ]; then
    if [ -f .cyberos/migrate-frs.sh ] && command -v node >/dev/null 2>&1; then
      echo "local-ci: regenerating docs/status …"
      bash .cyberos/migrate-frs.sh --page "$root" >/dev/null
    fi
  fi
  if [ -x scripts/check-status-sync.sh ]; then
    bash scripts/check-status-sync.sh
  fi
fi

# ── 2) Version consistency ──────────────────────────────────────────────────
# Product version = root package.json "version". CyberOS payload version = .cyberos/VERSION
# (intentionally different). Sync check: if VERSION file exists at root, it must match package.json.
if [ "${SKIP_VERSION:-0}" != "1" ]; then
  if [ -f package.json ] && command -v node >/dev/null 2>&1; then
    pkg_ver="$(node -e 'console.log(JSON.parse(require("fs").readFileSync("package.json","utf8")).version||"")')"
    echo "local-ci: product version (package.json)=$pkg_ver"
    if [ -f VERSION ]; then
      root_ver="$(tr -d ' \n\r' < VERSION)"
      if [ -n "$root_ver" ] && [ "$root_ver" != "$pkg_ver" ]; then
        echo "local-ci: ERROR VERSION ($root_ver) != package.json version ($pkg_ver)" >&2
        exit 1
      fi
      echo "local-ci: VERSION file matches package.json"
    fi
    if [ -f BUILD_NUMBER ]; then
      bn="$(tr -d ' \n\r' < BUILD_NUMBER)"
      echo "local-ci: BUILD_NUMBER=$bn (informational)"
    fi
    if [ -f .cyberos/VERSION ]; then
      cy="$(tr -d ' \n\r' < .cyberos/VERSION)"
      echo "local-ci: CyberOS payload version=.cyberos/VERSION=$cy (platform, not product)"
    fi
  fi
fi

# ── 3) Lint ─────────────────────────────────────────────────────────────────
if [ "${SKIP_LINT:-0}" != "1" ]; then
  if [ "$lane_py" = "1" ] && command -v uv >/dev/null 2>&1; then
    echo "local-ci: ruff check + format --check"
    uv run ruff check
    uv run ruff format --check
  fi
  if [ "$lane_rs" = "1" ] && command -v cargo >/dev/null 2>&1; then
    echo "local-ci: cargo fmt --check + clippy"
    cargo fmt --all -- --check
    cargo clippy --workspace --all-targets -- -D warnings
  fi
  if [ "$lane_web" = "1" ] && [ -f apps/web/package.json ]; then
    echo "local-ci: web eslint + tsc"
    if command -v pnpm >/dev/null 2>&1; then
      (cd apps/web && pnpm exec eslint . --max-warnings 0)
      (cd apps/web && pnpm exec tsc --noEmit)
    fi
  fi
fi

# ── 4) Build ────────────────────────────────────────────────────────────────
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  if [ "$lane_rs" = "1" ] && command -v cargo >/dev/null 2>&1; then
    echo "local-ci: cargo build --workspace"
    cargo build --workspace
  fi
  if [ "$lane_web" = "1" ] && [ "${LOCAL_CI_WEB_BUILD:-0}" = "1" ] && command -v pnpm >/dev/null 2>&1; then
    echo "local-ci: pnpm --filter web build"
    pnpm --filter web build
  fi
  if [ "${SKIP_COMPOSE:-0}" != "1" ] && command -v docker >/dev/null 2>&1; then
    if [ -f deploy/compose/docker-compose.local.yml ]; then
      echo "local-ci: docker compose local config"
      docker compose -f deploy/compose/docker-compose.local.yml config --quiet
    fi
    if [ -f deploy/compose/docker-compose.staging.yml ]; then
      echo "local-ci: docker compose staging config"
      docker compose -f deploy/compose/docker-compose.staging.yml config --quiet || true
    fi
  fi
fi

# ── 5) Tests ────────────────────────────────────────────────────────────────
if [ "${SKIP_TEST:-0}" != "1" ]; then
  if [ "$lane_py" = "1" ] && command -v uv >/dev/null 2>&1; then
    echo "local-ci: pytest -q"
    uv run pytest -q --tb=line
  fi
  if [ "$lane_rs" = "1" ] && command -v cargo >/dev/null 2>&1; then
    echo "local-ci: cargo test --workspace"
    cargo test --workspace --quiet
  fi
  if [ "$lane_web" = "1" ] && command -v pnpm >/dev/null 2>&1; then
    echo "local-ci: pnpm --filter web test"
    pnpm --filter web test
  fi
fi

# ── 6) act (local GitHub Actions for ci.yml only) ───────────────────────────
# Other workflows (deploy-vps) may be invalid under act schema — pin -W ci.yml.
if [ "${SKIP_ACT:-0}" != "1" ] && [ "${LOCAL_CI_FULL:-0}" = "1" ]; then
  if command -v act >/dev/null 2>&1; then
    echo "local-ci: act push -W .github/workflows/ci.yml -j status-sync (LOCAL_CI_FULL=1)"
    # Non-interactive: ensure ~/.actrc maps ubuntu-latest (see docs/deploy/local-ci-hooks.md)
    act push -W .github/workflows/ci.yml \
      --container-architecture "${ACT_ARCH:-linux/amd64}" \
      -j status-sync
    if [ "${LOCAL_CI_ACT_ALL:-0}" = "1" ]; then
      echo "local-ci: act full ci.yml matrix (LOCAL_CI_ACT_ALL=1)"
      act push -W .github/workflows/ci.yml --container-architecture "${ACT_ARCH:-linux/amd64}"
    fi
  else
    echo "local-ci: WARN act not installed — brew install act  (or SKIP_ACT=1)" >&2
  fi
elif [ "${SKIP_ACT:-0}" != "1" ] && command -v act >/dev/null 2>&1; then
  echo "local-ci: act available — list: act -l -W .github/workflows/ci.yml  (run: LOCAL_CI_FULL=1)"
  act -l -W .github/workflows/ci.yml 2>/dev/null || true
fi

echo "local-ci: OK"
