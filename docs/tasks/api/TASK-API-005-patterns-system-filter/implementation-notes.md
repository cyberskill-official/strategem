# TASK-API-005 — implementation notes

`ready_to_review` — **HITL required**. Agent will not set `done`.

## What landed (2026-07-27)

- Confirmed `list_patterns` already applies `system or he` with Vietnamese alias map; clarified Query descriptions (`system` canonical, `he` alias).
- Extended `tests/test_knowledge_patterns_cov019.py`: alias parity (`ky_mon` / `he=qimen`) + unknown → empty 200.
- Hardened `scripts/smoke-prod-full.sh`: compare filtered vs unfiltered `total`; assert every returned row `system == qimen`.
- Documented route + four query params in `docs/contracts/openapi-v1.md`.
- Patterns UI now sends `system=` when a filter is selected.
- Live-truth-audit deferred finding annotated as remediated (trail kept, not deleted).

## Evidence for reviewer

```bash
cd packages/tamthuc_api && uv run pytest tests/test_knowledge_patterns_cov019.py -q
# optional: API_BASE=https://api.strategem.cyberskill.world bash scripts/smoke-prod-full.sh
```

## HITL next

Reviewer: diff vs §1 + AC matrix → `ready_to_test` on human approval. Final `done` only after tester + human acceptance.
