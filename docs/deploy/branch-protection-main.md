# Branch protection for `main` (TT-006)

Do **not** apply until local/CI gates are green. Never push/merge without an operator instruction.

## Required checks (names must match GitHub Actions job names)

From `.github/workflows/`:

| Workflow | Required check name (typical) |
|---|---|
| `ci.yml` | `rust` / `python` / `web` / `status-sync` |
| `security-scan.yml` | security scan job |
| `dependency-scan.yml` | dependency scan job |
| `cd.yml` | integration/build jobs that should gate merge (not prod deploy) |

Confirm exact check names with:

```bash
gh api repos/cyberskill-official/strategem/commits/main/status --jq .
gh api repos/cyberskill-official/strategem/actions/runs --jq '.workflow_runs[:5] | .[] | {name,conclusion,head_branch}'
# Or open a PR and copy the check run names from the Checks tab.
```

## Apply via API (repo admin)

```bash
OWNER=cyberskill-official
REPO=strategem

gh api -X PUT "repos/${OWNER}/${REPO}/branches/main/protection" \
  -H "Accept: application/vnd.github+json" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "rust",
      "python",
      "web",
      "status-sync"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
EOF
```

After applying, add Security scan + dependency-scan contexts once their job `name:` values are confirmed.

## Verify

```bash
gh api "repos/${OWNER}/${REPO}/branches/main/protection"
```

Expect a policy object (not HTTP 404). A PR with a failing required check must not be mergeable.

## Also configure (UI / LIM-08)

1. GitHub Environment `production`: required reviewers before deploy.
2. Optional follow-ups: `CODEOWNERS`, PR template referencing the two CyberOS HITL gates.
