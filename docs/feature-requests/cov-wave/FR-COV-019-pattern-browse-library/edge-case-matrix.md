# edge-case-matrix@1 — COV-019

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | SEED | list all | ≥150 patterns | test_list_patterns_seeded |
| E2 | FILTER | he=qimen | only qimen | test_filter_by_he_and_search |
| E3 | VOICE | no prophecy | blocked phrases stripped | test_filter_by_he_and_search |
| E4 | WEB | /patterns | page + API | palace-lunar-patterns smoke |
