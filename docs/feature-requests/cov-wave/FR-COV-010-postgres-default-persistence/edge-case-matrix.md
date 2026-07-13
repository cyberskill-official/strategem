# edge-case-matrix@1 — COV-010

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | CONFIG | DATABASE_URL set | backend=postgres | test_postgres_cast_get_survives_new_service |
| E2 | CONFIG | no URL, non-prod | backend=memory | test_dev_allows_memory_without_database_url |
| E3 | SECURITY | APP_ENV=production, no URL | RuntimeError fail-closed | test_prod_fail_closed_without_database_url |
| E4 | PERSIST | cast then new service instance | get_query_result returns charts | test_postgres_cast_get_survives_new_service |
| E5 | API | calculate → GET /queries/{id} | 200 same query_id + chart | test_api_calculate_get_query_with_postgres |
| E6 | DEGRADATION | Postgres down | tests skip or raise at connect | pytest.skip path |
| E7 | DATA | report_id lookup | get_report returns payload | test_postgres_cast_get_survives_new_service |
| E8 | DOCS | migrate documented | local-docker + SHIP_CHECKLIST | manual / runbook asserts |
