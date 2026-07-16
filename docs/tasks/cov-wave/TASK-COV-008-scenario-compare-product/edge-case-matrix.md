# edge-case-matrix@1 — COV-008

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | HAPPY | 2 scenarios | 200 + ranked_labels | test_scenario_compare_returns_ranked |
| E2 | BOUNDS | 1 scenario | 400 | test_scenario_compare_rejects_one |
| E3 | DETERMINISM | optimizer reuse | no invent scores | strat test_ranking_by_best_score |
| E4 | VOICE | disclaimer | present | test_scenario_compare_returns_ranked |
| E5 | WEB | /scenarios form | testids | scenarios-cross-cov008-012.test.mjs |
