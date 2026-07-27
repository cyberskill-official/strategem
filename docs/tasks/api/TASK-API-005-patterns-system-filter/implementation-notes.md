# TASK-API-005 — implementation notes

`testing` — claimed 2026-07-27. Coverage-gate + TRACE-004 + prod smoke recorded. **Halt for final human acceptance** (`testing` → `done`). Agent will not set `done`.

## What landed (2026-07-27)

- Confirmed `list_patterns` already applies `system or he` with Vietnamese alias map; clarified Query descriptions (`system` canonical, `he` alias).
- Extended `tests/test_knowledge_patterns_cov019.py`: alias parity (`ky_mon` / `he=qimen`) + unknown → empty 200.
- Hardened `scripts/smoke-prod-full.sh`: compare filtered vs unfiltered `total`; assert every returned row `system == qimen`.
- Documented route + four query params in `docs/contracts/openapi-v1.md`.
- Patterns UI now sends `system=` when a filter is selected.
- Live-truth-audit deferred finding annotated as remediated (trail kept, not deleted).

## Testing evidence (2026-07-27)

```bash
cd packages/tamthuc_api && uv run pytest tests/test_knowledge_patterns_cov019.py -q
# 5 passed

API_BASE=https://api.strategem.cyberskill.world bash scripts/smoke-prod-full.sh
# patterns filter system=qimen total=105 (of 175) rows=105
```

- Coverage gate artefact: `coverage-gate.md` (outcome PASS; TRACE-004 closed)
- awh / caf: N/A (no module goldenset / CAF seal)
- Transition receipt: `docs/tasks/_state/receipts/TASK-API-005--ready_to_test--testing--05cb0bad7efc.json`

## HITL

- Review acceptance: **APPROVED** 2026-07-27 → `ready_to_test`
  - Evidence: `hitl-review-acceptance.md`
  - Packet: `code-review.md`
  - Verdict artifact + transition receipts under `docs/tasks/_verdicts/` and `docs/tasks/_state/receipts/`
- Final `done` only after human acceptance (`testing` → `done`).
  - Operator phrase: **`ACCEPT TASK-API-005`** (or equivalent final-accept utterance)
