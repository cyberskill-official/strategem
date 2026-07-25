# Oracle certification status (COV-001 + W4)

Machine-readable + human report for engine trust gates.

## Two tracks (do not conflate)

| Track | Location | Meaning |
|-------|----------|---------|
| **Self-oracle regression** | `crates/*/tests/fixtures/*_cert_v1.csv` | `oracle_source=engine_golden_v1+cast_cli` — deterministic lock against current engines. Not kin* certification. |
| **External oracle (W4)** | `oracle/{kinqimen,kinliuren,kintaiyi,sxwnl}/` | Independent dumps. `sample/` = harness proof; `full/` = gate when present, **SKIP** when absent. |

See [`oracle/README.md`](../../oracle/README.md) and [`oracle/FORMAT.md`](../../oracle/FORMAT.md).

## Self-oracle suite inventory

| System | Fixture | Min cases | Gate | Test |
|--------|---------|----------:|------|------|
| QiMen | `crates/cyberos-qimen/tests/fixtures/qimen_cert_v1.csv` | 30 | `cache_key` match + double-cast | `certification_suite` |
| LiuRen | `crates/cyberos-luchnham/tests/fixtures/liuren_cert_v1.csv` | 30 | `cache_key` match + double-cast | `certification_suite` |
| TaiYi | `crates/cyberos-thaiat/tests/fixtures/taiyi_cert_v1.csv` | 20 | `cache_key` match + double-cast | `certification_suite` |
| Tiet khi | `crates/cyberos-lichphap/tests/fixtures/tietkhi_cert_multiyear.csv` | 50 | \|Δt\| < 60s vs fixture | `tietkhi_certification` |
| Calendar harness | CORE-006 fixtures | multi-decade self | CI `core-oracle.yml` | `oracle_harness` |

## External suite inventory (W4)

| Source | Sample (always) | Full (gate or SKIP) | Test |
|--------|-----------------|---------------------|------|
| kinqimen | `oracle/kinqimen/sample/dinh_cuc.csv` | `oracle/kinqimen/full/dinh_cuc.csv` | `external_oracle_cert` |
| kinliuren | `oracle/kinliuren/sample/khoa_the.csv` | `oracle/kinliuren/full/khoa_the.csv` | `external_oracle_cert` |
| kintaiyi | `oracle/kintaiyi/sample/van_xuong.csv` | `oracle/kintaiyi/full/van_xuong.csv` | `external_oracle_cert` |
| sxwnl | `oracle/sxwnl/sample/tietkhi.csv` | `oracle/sxwnl/full/tietkhi.csv` | `external_oracle_cert` |

## CI

- Workflow: `.github/workflows/oracle-certification.yml`
- Local self-oracle: `cargo test -p cyberos-qimen --test certification_suite` (and peers)
- Local external: `cargo test -p cyberos-qimen --test external_oracle_cert` (and peers)

## Report artefact

See `report.json` in this directory (regenerated when suite counts change).
