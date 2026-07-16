# edge-case-matrix@1 — COV-002

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | NULL | Missing co_truong_phai in request | stamp default object (never empty omit) | test_flag_stamp_cov002 + flag_stamp_cov002.rs |
| E2 | NULL | Missing co_lich_phap in request | stamp tz/longitude + stamped:true | test_flag_stamp_cov002 + engines |
| E3 | DETERMINISM | Same dau_vao + flags | identical provenance.cache_key path | LocalEngineClient cache_key over stamped lich |
| E4 | BOUNDS | All three he (ky_mon, luc_nham, thai_at) | both flag objects present | test_local_engine_stamps_all_three_systems |
| E5 | DEGRADATION | cast-cli omits stamp | LocalEngineClient fills default/source | engine.py _cast_via_cli |
| E6 | SECURITY | No silent school switch | stamped flags visible in API chart payload | calculate → charts.*.co_truong_phai |
| E7 | REGRESSION | Rust engine defaults | co_lich_phap.stamped true + school keys | flag_stamp_cov002.rs ×3 crates |
| E8 | STUB | StubEngineClient | non-empty stamps for CI | StubEngineClient.cast |
