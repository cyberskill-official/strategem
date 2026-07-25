# External oracle datasets (Wave W4)

This directory is the **only** place for independent external reference dumps used
to certify classical engines. It is deliberately separate from
`crates/*/tests/fixtures/*_cert_v1.csv`, which are **self-oracle regression**
goldens (`oracle_source=engine_golden_v1+cast_cli`) and must never be relabeled
as kinqimen / kinliuren / kintaiyi / sxwnl certification.

## Layout

```
oracle/
  README.md                 ← this file
  FORMAT.md                 ← CSV/JSON column contracts
  kinqimen/{sample,full}/   ← QiMen (kinqimen)
  kinliuren/{sample,full}/  ← LiuRen (kinliuren)
  kintaiyi/{sample,full}/   ← TaiYi (kintaiyi)
  sxwnl/{sample,full}/      ← lichpháp 24×N solar-term dumps
```

| Subdir | Role | In git? |
|--------|------|---------|
| `sample/` | Tiny hand-verifiable classical rows **with cited sources**. Proves the harness matches external/classical data end-to-end. **Not** full certification. | Yes |
| `full/` | Real dumps at stated sample sizes. When present, Rust tests **gate** (100% match). When absent, tests **SKIP** with an honest message. | README only; `*.csv` / `*.json` gitignored |

## Where real dumps come from

| Source | Upstream | Typical dump |
|--------|----------|--------------|
| kinqimen | [kinqimen](https://pypi.org/project/kinqimen/) (Python) | Chart / `dinh_cuc` / plate rows across flag combinations |
| kinliuren | [kinliuren](https://pypi.org/project/kinliuren/) | `khoa_the` catalog + thiệp-hại edge cases |
| kintaiyi | [kintaiyi](https://pypi.org/project/kintaiyi/) | Văn xương / toán / bát tướng across epochs |
| sxwnl | [sxwnl](https://github.com/ytliu0/ChineseCalendar) / tyme4py | Multi-decade 24×N jieqi UTC instants |

Generate dumps **offline** (not as Cargo deps). Document the generator command,
library version, and dump date in a `#` comment header of each CSV (see
[`FORMAT.md`](FORMAT.md)).

## How to drop a full dump

1. Produce CSV matching the contract in `FORMAT.md` for that source.
2. Place it under `oracle/<source>/full/<filename>.csv` (filenames listed in each
   source README).
3. Run `cargo test -p cyberos-<engine> --test external_oracle_cert`.
4. The previously-skipping full-cert test will assert 100% match at that dump’s
   sample size. Do **not** invent or pad rows to turn the skip into a green lie.

## What is still pending (honest status)

Until real dumps land under `full/`:

- QiMen sieu-than / tiếp-khí / chai-bu·zhi-run·mao-shan **boundary divergence set vs kinqimen**
- LiuRen **full khoa_the catalog** + kinliuren thiệp-hại edge cases
- TaiYi **kintaiyi** match on văn xương / toán / bát tướng across epochs
- lichpháp **multi-decade sxwnl 24×N** gate (TASK-CORE-006); current published
  equinox/solstice AC samples are not a full sxwnl dump

The committed `sample/` rows prove the harness; they do **not** close those gaps.
