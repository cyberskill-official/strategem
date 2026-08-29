# Branch protection for `main` + production Environment (TT-006 / D-CD-001)

Do **not** apply until local/CI gates are green. Never push/merge without an operator instruction.

Agents can open PRs that *enable* `environment: production` in workflows; they **cannot** configure GitHub Environment reviewers or branch protection for you. Complete the HITL checklist below in the GitHub UI (or via the documented API for branch protection only).

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

## Apply branch protection via API (repo admin)

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

`enforce_admins: true` keeps admins under the same rules. Do not turn admin bypass back on to “unblock” a merge.

## Verify branch protection

```bash
gh api "repos/${OWNER}/${REPO}/branches/main/protection"
```

Expect a policy object (not HTTP 404). A PR with a failing required check must not be mergeable.

## Operator HITL — GitHub Environment `production` (D-CD-001)

`.github/workflows/deploy-vps.yml` uses `environment: production` on the SSH deploy job. Until reviewers are configured, Environment protection is incomplete.

### Exact clicks (GitHub UI)

1. Open **https://github.com/cyberskill-official/strategem/settings/environments**
2. Create or open the environment named exactly **`production`** (name must match the workflow).
3. Under **Deployment protection rules**:
   - Enable **Required reviewers**
   - Add one or more **named people or teams** who may approve VPS prod rolls
   - Optionally set a **Wait timer** (extra delay after approval)
4. Save. Do **not** rely on “prevent self-review” alone without named reviewers.
5. Confirm Environment secrets used by deploy (`VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`) live on this environment or the repo, per your secret layout.
6. Optional: create a separate **`staging`** environment for `cd.yml`’s staging record job (already referenced).

### What approval looks like

On push to `main` (matching deploy paths) or `workflow_dispatch`, the **build-and-push** job may run and publish to GHCR. The **deploy** job stays **Waiting** until a configured reviewer approves the Environment deployment in the Actions run UI.

### Policy notes

- Prefer **named reviewers**; document who is on-call for prod rolls in your ops channel.
- Keep branch protection `enforce_admins: true` aligned with Environment reviewers — do not document or enable admin-only shortcuts that skip review.
- Immutable roll: deploy pins `API_IMAGE` by **digest** (`image@sha256:…`), not floating `:main` (D-IMAGE-001 alignment). See `docs/deploy/cd-split.md` and `docs/deploy/vps-api.md`.

## Also configure

1. Branch protection actually applied (API above or Settings → Branches → `main`).
2. Optional follow-ups: `CODEOWNERS`, PR template referencing the two CyberOS HITL gates (`reviewing → ready_to_test`, `testing → done`).
