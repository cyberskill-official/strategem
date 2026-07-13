# edge-case-matrix@1 — COV-018

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | GREGORIAN | datetime | convert ok | test_gregorian_convert |
| E2 | BAZI | valid pillars | tu_tru authoritative | test_bazi_convert_and_validation |
| E3 | BAZI | bad pillar | VI error | test_bazi_convert_and_validation |
| E4 | LUNAR | server convert | client_invented false | test_lunar_convert_server_side |
| E5 | LUNAR | out of range | 400 VI | test_api_calendar_convert_vi_errors |
| E6 | WEB | three modes | chips + convert API | query-form + smoke |
