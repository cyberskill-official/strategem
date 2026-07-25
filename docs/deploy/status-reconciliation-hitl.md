# Status & CyberOS tracking reconciliation (TT-004 / TT-005)

**HITL required.** Agents must not mark tasks `done` or force-add secrets/memory.

## Conflicting status sources (do not trust 100% claims)

| Source | Claim | Notes |
|---|---|---|
| `docs/tasks/**/spec.md` frontmatter | Many/all `status: done` | Agent-editable; CyberOS says humans set `done` |
| `docs/status/index.html` | Aggregated “done” counts | Derived from frontmatter — inherits self-report |
| `docs/tasks/backlog.yaml` | Mostly `blocked` | Stale header (`generated: 2026-07-08`) |
| `docs/tasks/IMPLEMENTATION_ORDER.md` | Mixed narrative | Not a single SoT |

Until a human reconciles these, treat **CI green + human acceptance** as the only release signal.

## LEGAL-004

Counsel sign-off record is missing (`docs/legal/counsel-signoff-record.md`). Spec frontmatter may say `done`, but **launch remains gated** by `docs/legal/vn-legal-review/sign-off-gate.md`. Do not flip LEGAL-004 to done without counsel.

Suggested human action: set LEGAL-004 frontmatter to `blocked` or `testing` with a note “awaiting counsel sign-off”, or leave as-is and treat sign-off gate as authoritative.

## CyberOS normative layer (TT-004)

`.gitignore` ignores all of `.cyberos/`. Normative files that should be **reviewable in git** (human decision on exact paths):

- Track (candidates): `AGENT-ENTRY.md`, `cuo/EXECUTION-DISCIPLINE.md`, `cuo/STATUS-REFERENCE.md`, `cuo/ship-tasks.md`, `cuo/gates/run-gates.sh`, `gates.env` (non-secret), skill sources, `mcp/` entrypoints
- Keep ignored: `memory/store/`, caches, render intermediates, secrets, tenant BRAIN data

Do **not** `git add -f` the whole `.cyberos/` tree. Prefer narrowing `.gitignore` under human approval and a bootstrap script that fails clearly on fresh clones.
