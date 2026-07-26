---
artefact: code-review@1
fr_id: TASK-API-005
module: api
class: improvement
status: human_approved
reviewer: ship-tasks (agent packet) + Stephen Cheng (HITL)
reviewed_at: 2026-07-27
impl_commit: bd15522ceff6f6922bf3519794cb96a8fa8cec56
human_verdict: APPROVE review TASK-API-005
human_verdict_at: 2026-07-27
transition: reviewing → ready_to_test
---

# Code review — TASK-API-005 (patterns `?system=` filter contract lock)

## Scope of diff

Commit `bd15522` — contract lock + acceptance hardening (filter already correct on prod):

| Path | Change |
|---|---|
| `packages/tamthuc_api/.../routes/knowledge.py` | Query docs: `system` canonical, `he` alias |
| `packages/tamthuc_api/tests/test_knowledge_patterns_cov019.py` | Alias parity + unknown → empty 200 |
| `scripts/smoke-prod-full.sh` | Hard-fail when filtered total/system drift |
| `docs/contracts/openapi-v1.md` | Document route + `system`/`he`/`q`/`limit` |
| `apps/web/app/patterns/page.tsx` | Send `system=` when filter selected |
| `docs/tasks/_audits/2026-07-25-live-truth-audit.md` | Remediation trail (not silent delete) |

## §1 / §4 → test map

| AC | Named evidence | Result |
|---|---|---|
| 1 System filter subsets | `test_filter_by_system_query_param` + smoke total/row asserts | pass (impl) |
| 2 Alias parity | `test_system_alias_ky_mon_matches_qimen` | pass (impl) |
| 3 Cross-system exclusion | `test_filter_by_system_query_param` (liuren path) | pass (impl) |
| 4 Unknown system empty | `test_unknown_system_returns_empty` | pass (impl) |
| 5 Smoke hard-fail | `scripts/smoke-prod-full.sh` patterns filter block | landed |
| 6 OpenAPI lists route | `docs/contracts/openapi-v1.md` | landed |
| 7 Audit trail closed | live-truth-audit dated TASK-API-005 note | landed |
| 8 UI filter | `apps/web/app/patterns/page.tsx` uses `system=` | landed |

## Recommendation

**Approve** review acceptance: `reviewing → ready_to_test`. Agent will not set `done`.

## Human gate (recorded)

Operator verdict (2026-07-27): **APPROVE review TASK-API-005**

Evidence: `docs/tasks/api/TASK-API-005-patterns-system-filter/hitl-review-acceptance.md`
