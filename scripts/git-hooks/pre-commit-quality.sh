#!/usr/bin/env bash
# WEB-020 — quality pre-commit (ruff + eslint on staged files).
# Install (chain with cyberos status hook):
#   cp scripts/git-hooks/pre-commit .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
set -euo pipefail

root="$(git rev-parse --show-toplevel)"
cd "$root"

# Pipefail-safe: materialize staged list once
staged="$(git diff --cached --name-only --diff-filter=ACMR || true)"
staged_py="$(grep -E '\.py$' <<<"$staged" || true)"
staged_web="$(grep -E '^apps/web/.*\.(ts|tsx|js|mjs|css)$' <<<"$staged" || true)"
staged_rs="$(grep -E '\.rs$' <<<"$staged" || true)"

fail=0

if [ -n "$staged_py" ]; then
  if command -v uv >/dev/null 2>&1; then
    echo "pre-commit-quality: ruff format --check (staged py)"
    # shellcheck disable=SC2086
    if ! uv run ruff format --check $staged_py; then
      echo "pre-commit-quality: run: uv run ruff format <files>" >&2
      fail=1
    fi
    echo "pre-commit-quality: ruff check (staged py)"
    # shellcheck disable=SC2086
    if ! uv run ruff check $staged_py; then
      fail=1
    fi
  else
    echo "pre-commit-quality: WARN uv not found — skip ruff" >&2
  fi
fi

if [ -n "$staged_web" ]; then
  if [ -f apps/web/package.json ]; then
    echo "pre-commit-quality: eslint (web)"
    if command -v pnpm >/dev/null 2>&1; then
      if ! (cd apps/web && pnpm exec eslint . --max-warnings 0); then
        fail=1
      fi
    elif [ -x apps/web/node_modules/.bin/eslint ]; then
      if ! (cd apps/web && ./node_modules/.bin/eslint . --max-warnings 0); then
        fail=1
      fi
    else
      echo "pre-commit-quality: WARN eslint not available — skip" >&2
    fi
  fi
fi

if [ -n "$staged_rs" ] && command -v cargo >/dev/null 2>&1; then
  echo "pre-commit-quality: cargo fmt --check (staged rust)"
  if ! cargo fmt --all -- --check; then
    echo "pre-commit-quality: run: cargo fmt --all" >&2
    fail=1
  fi
fi

if [ "$fail" -ne 0 ]; then
  echo "pre-commit-quality: FAILED" >&2
  exit 1
fi
echo "pre-commit-quality: ok"
exit 0
