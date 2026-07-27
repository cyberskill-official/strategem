---
artefact: coverage-gate@1
fr_id: TASK-API-005
outcome: PASS
tests_failed: 0
tested_at: 2026-07-27
---

# Coverage gate — TASK-API-005

## Command

```
cd packages/tamthuc_api && uv run pytest tests/test_knowledge_patterns_cov019.py -q \
  --cov=tamthuc_api.routes.knowledge --cov-report=term-missing
```

## Result

```
.....                                                                    [100%]
5 passed
packages/tamthuc_api/src/tamthuc_api/routes/knowledge.py   47% file-level
```

File-level 47% is expected: this module also hosts COV-022 graph neighbors/nodes handlers that TASK-API-005 did not modify. The `list_patterns` filter contract (canonical `system=`, `he=` alias, unknown → empty) is exercised by all five named tests below. Uncovered lines are graph routes + rare `_load_patterns` edge paths (non-dict row / prophecy strip / loader exception).

Additional gates:

| Gate | Outcome |
|---|---|
| Task pytest (above) | **PASS** 5/5 |
| `LOCAL_CI_QUICK=1` local-ci | **PASS** |
| Prod smoke `API_BASE=https://api.strategem.cyberskill.world bash scripts/smoke-prod-full.sh` | **PASS** — `patterns filter system=qimen total=105 (of 175) rows=105` |
| Merge push CI (impl+review commits) | **PASS** — CI, CD, Deploy VPS API, Security scan, product-journeys |
| awh | **N/A** (no `modules/API/.awh/` / sealed goldenset) |
| caf | **N/A** (no `packages/tamthuc_api/audit-profile.yaml` / `.caf/` seal) |
| `.cyberos/cuo/gates/run-gates.sh` coverage autodetection | **env RED** — bare `coverage run -m pytest` lacks venv deps (`reportlab`); not a TASK-API-005 regression (local-ci + task pytest green) |

## TRACE-004 (§1 clause / §4 AC → test)

| Clause / AC | Named evidence | Status |
|---|---|---|
| §1 #1 / AC1 System filter subsets | `test_filter_by_system_query_param` + prod smoke total/row asserts | **passed** |
| §1 #1 / AC2 Alias parity | `test_system_alias_ky_mon_matches_qimen` | **passed** |
| §1 #1 / AC3 Cross-system exclusion | `test_filter_by_system_query_param` (liuren path) | **passed** |
| §1 #2 / AC4 Unknown system empty | `test_unknown_system_returns_empty` | **passed** |
| §1 #4 / AC5 Smoke hard-fail | `scripts/smoke-prod-full.sh` patterns filter block (prod run 2026-07-27) | **passed** |
| §1 #3 / AC6 OpenAPI lists route | `docs/contracts/openapi-v1.md` (`system`/`he`/`q`/`limit`) | **passed** (landed) |
| §1 #6 / AC7 Audit trail closed | live-truth-audit dated TASK-API-005 remediation note | **passed** (landed) |
| §1 #5 / AC8 UI filter | `apps/web/app/patterns/page.tsx` sends `system=` | **passed** (landed) |

## Module gates

- awh: N/A
- caf: N/A

## files_below_90pct

- `packages/tamthuc_api/src/tamthuc_api/routes/knowledge.py` — 47% file-level; uncovered = out-of-scope COV-022 graph handlers + rare loader edges (not part of this contract-lock scope)
