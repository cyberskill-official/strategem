# edge-case-matrix@1 — COV-004

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | BOUNDS | Catalog size | ≥40 named rows with citations | catalog_has_at_least_40_named_with_citations |
| E2 | DETECTION | 15 high-priority pairs | each id detected at correct cung | detect_at_least_15_high_priority_on_goldens |
| E3 | SECURITY | Am lineage | no invented polarity/hits | no_polarity_without_rule_match_empty_am |
| E4 | ORDER | 戊丙 vs 丙戊 | distinct ordered pairs | ordered_stem_pairs |
| E5 | DATA | JSON loads | ≥40 parse | patterns_json_loads |
| E6 | WEB | Vernacular first | glossary maps classical → VI | pattern-vernacular-cov004.test.mjs |
| E7 | DEGRADATION | Unknown pair not in catalog | no hit for that pair | match_ordered only catalog |
| E8 | REGRESSION | mon_bach / phuc / phan still emit | special rules retained | detect_cach_cuc + existing oracle |
