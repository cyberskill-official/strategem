# edge-case-matrix@1 — COV-006

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | ALWAYS | chu/khach toan + truong_doan | present on ban | cac_toan_and_chu_khach_always_present |
| E2 | FLAGS | epoch × dem_toan × duong | envelope stamps | epoch_and_dem_toan_flag_combinations |
| E3 | DETECTION | golden years scan | ≥1 non-empty cach_cuc | golden_years_may_emit_nonempty_cach_when_conditions_met |
| E4 | VOICE | no winner field | winner absent on hits | golden_years… |
| E5 | WEB | empty TA story | dedicated empty copy | taiyi-story-cov006.test.mjs |
| E6 | WEB | vernacular TA names | glossary 掩/擊… | taiyi-story-cov006.test.mjs |
