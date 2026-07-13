# edge-case-matrix@1 — COV-012

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | HAPPY | 3 systems | reads with stance | test_cross_system_validate_three_columns |
| E2 | SECURITY | no merged_score | field absent | test_cross_system_validate_three_columns |
| E3 | STRAT | agree/diverge pure | stance_from_cach_cuc | test_cross_system.py |
| E4 | WEB | three columns | cross-system page | scenarios-cross-cov008-012.test.mjs |
| E5 | VOICE | soft VI summary | summary_vi | API response |
