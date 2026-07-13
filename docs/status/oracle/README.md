# Oracle certification status (COV-001)

Machine-readable + human report for dual-benchmark engine trust gates.

## Suite inventory

| System | Fixture | Min cases | Gate | Test |
|--------|---------|----------:|------|------|
| QiMen | `crates/cyberos-qimen/tests/fixtures/qimen_cert_v1.csv` | 30 | `cache_key` match + double-cast | `certification_suite` |
| LiuRen | `crates/cyberos-luchnham/tests/fixtures/liuren_cert_v1.csv` | 30 | `cache_key` match + double-cast | `certification_suite` |
| TaiYi | `crates/cyberos-thaiat/tests/fixtures/taiyi_cert_v1.csv` | 20 | `cache_key` match + double-cast | `certification_suite` |
| Tiet khi | `crates/cyberos-lichphap/tests/fixtures/tietkhi_cert_multiyear.csv` | 50 | \|Δt\| < 60s vs fixture | `tietkhi_certification` |
| Calendar harness | CORE-006 fixtures | multi-decade | CI `core-oracle.yml` | `oracle_harness` |

## Oracle / flag documentation

Each CSV row carries:

- `oracle_source` — currently `engine_golden_v1+cast_cli` (deterministic regression goldens locked from `cast-cli` + in-process engines). External kinqimen/kinliuren/kintaiyi row-level ports remain additive; partial kin* CSVs under module `tests/fixtures/*kin*.csv` still run in module oracles.
- `flags_doc` — school flags used for the case (dingju/pan for QiMen; quy_nhan for LiuRen; epoch/cap for TaiYi).

Default flag assumptions for cert_v1 (must match `crates/cast-cli` mapping):

| System | Flags |
|--------|--------|
| QiMen | `yin_yang=duong`, `zhong_gong_ky=khon2`, `chan_thai_duong_thoi=true`; dingju/pan vary per row |
| LiuRen | `quy_nhan=giap_mau_canh` (cast-cli current default) |
| TaiYi | `cap=nien`, `dem_toan=truoc_thai_at`, `duong_don=true`; epoch varies |

## CI

- Workflow: `.github/workflows/oracle-certification.yml`
- Local: `cargo test -p cyberos-qimen --test certification_suite` (and peers above)

## Report artefact

See `report.json` in this directory (regenerated when suite counts change).
