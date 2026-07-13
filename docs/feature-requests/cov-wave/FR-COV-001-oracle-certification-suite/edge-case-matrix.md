# edge-case-matrix@1 — COV-001

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | BOUNDS | QiMen 36-case matrix spans dingju×pan | all cache_keys match fixture | certification_suite qimen |
| E2 | BOUNDS | LiuRen 30-case can×chi grid | all cache_keys match | certification_suite liuren |
| E3 | BOUNDS | TaiYi 24-case year×epoch | all cache_keys match | certification_suite taiyi |
| E4 | TIME | Tiet khi 120 terms 2018–2022 | \|err\| < 60s | tietkhi_certification |
| E5 | DETERMINISM | Double-cast same input | identical cache_key | all cert suites |
| E6 | SECURITY | Fixtures committed; no network oracle at test time | offline CI | oracle-certification.yml |
| E7 | DEGRADATION | Missing fixture file | test fails fail-closed | fs::read_to_string expect |
| E8 | REGRESSION | Engine flag default drift vs cast-cli | cache_key mismatch fails suite | flags_doc in CSV |
