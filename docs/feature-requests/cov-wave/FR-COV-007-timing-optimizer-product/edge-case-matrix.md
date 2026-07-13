# edge-case-matrix@1 — COV-007

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | HAPPY | Range with top_n=3 | 200 + ranked windows + reasons | test_timing_optimize_returns_windows |
| E2 | BOUNDS | end < start | 400 VALIDATION_ERROR | test_timing_optimize_rejects_inverted_range |
| E3 | DETERMINISM | Same request twice | identical scores (strat unit) | test_deterministic |
| E4 | DEGRADATION | No LLM for scores | ai_disclosure.used_llm false | test_timing_optimize_returns_windows |
| E5 | VOICE | Disclaimer present | body.disclaimer non-empty | test_timing_optimize_returns_windows |
| E6 | WEB | /timing form + i18n | page + vi keys | timing-page.test.mjs |
| E7 | E2E | Live optimize when API up | windows length ≥1 | e2e-live-smoke.mjs |
| E8 | SECURITY | top_n clamped 1..20 | no huge scan abuse | timing.py max(1,min(top_n,20)) |
