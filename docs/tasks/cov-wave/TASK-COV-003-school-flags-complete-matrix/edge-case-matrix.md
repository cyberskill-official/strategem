# edge-case-matrix@1 — COV-003

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | FLAG | dingju maoshan | option present | school-flags-cov003.test.mjs |
| E2 | FLAG | zhong_gong_ky | khon2 / giu_nguyen | school-flags.ts + form |
| E3 | FLAG | dem_toan | truoc/sau thai at | school-flags.ts |
| E4 | I18N | vi labels | not English-only | vi.json settings.flag.* |
| E5 | PAYLOAD | toCastPayloadFlags | flat keys for engine | school-flags.ts |
| E6 | RESULTS | tech details | stamped flags JSON | results-panel stamped-flags |
