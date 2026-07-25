# External oracle CSV/JSON format (W4)

All datasets under `oracle/` share these rules:

1. UTF-8 text. `#` starts a comment (full-line only).
2. First non-comment line is a CSV header of column names.
3. Required metadata comments (recommended at top):

```
# kind: sample | full
# source: <library-or-classical-cite> <version-or-section>
# generated: YYYY-MM-DD   (full dumps)
# scope: harness proof only | full certification gate
```

4. Do **not** put `oracle_source=engine_golden_v1+cast_cli` here. That label
   belongs only to self-oracle regression fixtures under `crates/*/tests/fixtures/`.

---

## kinqimen — `dinh_cuc.csv`

| Column | Type | Notes |
|--------|------|-------|
| `term_index` | u8 0..24 | Lap-Xuân origin (0 = Lập Xuân) |
| `branch_index` | u8 0..12 | Hour branch for phù-đầu nguyên |
| `method` | `chaibu` \| `zhirun` \| `maoshan` | Dingju school |
| `tri_nhuan` | 0 \| 1 | Chỉ-nhuận flag (zhirun only) |
| `so_cuc` | u8 1..9 | Expected cục số |
| `duong_don` | 0 \| 1 | Dương độn |
| `nguyen` | u8 1..3 | Thượng / trung / hạ |
| `cite_note` | string | Optional; sample rows should cite classical locus |

Full dumps may add plate columns later (`truc_phu`, `dia_ban`, …) without
breaking this prefix.

## kinliuren — `khoa_the.csv`

| Column | Type | Notes |
|--------|------|-------|
| `nguyet_tuong` | Chi roman | `Ty` `Suu` … `Hoi` (`Ty2` = Tỵ 巳) |
| `gio_chiem` | Chi roman | |
| `can_ngay` | Can roman | `Giap` … `Quy` |
| `chi_ngay` | Chi roman | |
| `expected_phap` | string | e.g. `PhucNgam` `PhanNgam` `ThiepHai` |
| `expected_khoa_the_han` | string | Han name, e.g. `伏吟` |
| `cite_note` | string | Classical cite for sample rows |

## kintaiyi — `van_xuong.csv`

| Column | Type | Notes |
|--------|------|-------|
| `nhap_cuc` | u8 1..72 | Số nhập cục |
| `duong_don` | 0 \| 1 | |
| `expected_ring` | u8 0..15 | Văn xương ring index |
| `cite_note` | string | Algorithm locus (e.g. Claude-04 §4.1) |

Full dumps may add `epoch`, `nam_ce`, `chu_toan`, `khach_toan`, `bat_tuong_*`.

## sxwnl — `tietkhi.csv`

| Column | Type | Notes |
|--------|------|-------|
| `year` | i32 | Gregorian |
| `term_index` | u8 0..24 | Lap-Xuân origin |
| `jd_utc` | f64 | Published / sxwnl UTC JD of the term |
| `cite_note` | string | Almanac or sxwnl provenance |

Gate: `|solve_term_instant − jd_utc| × 86400 < 60` seconds (tập-5 AC band).

## JSON (optional)

A future dump may use JSON arrays of objects with the same field names. The
current harness loads CSV only; JSON support can be added without changing
column contracts.
