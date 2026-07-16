---
id: WEB-020
title: Pre-commit quality hook + CI parity
status: done
class: improvement
priority: MUST
depends_on: []
---

# WEB-020

## Goal
Catch ruff format and eslint failures before push; CI web gate runs CSS smoke after build.

## §1
1. Repo script `scripts/git-hooks/pre-commit-quality.sh` runs ruff format --check / ruff check on staged py, eslint on staged web ts/tsx when present.
2. Document install into `.git/hooks/pre-commit` (chain with cyberos status hook).
3. CI web job runs css-story-smoke after build.
