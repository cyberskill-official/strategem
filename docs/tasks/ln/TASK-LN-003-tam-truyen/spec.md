---
id: TASK-LN-003
title: "Chin tong mon + tam truyen - nine-method decision tree (賊剋/比用/涉害/遙剋/昴星/別責/八專/伏吟/返吟) selecting so/trung/mat truyen, phuc ngam and phan ngam checked first; emits tam_truyen into the la so ban for he=luc_nham"
module: LN
priority: MUST
status: done
phase: P1
slice: 3
lang: rust
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-02 s4, Claude-02 s9.1, Grok-29]
related_frs: [TASK-LN-001, TASK-LN-002, TASK-LN-004, TASK-LN-005, TASK-LN-006, TASK-CORE-007, TASK-PLAT-002]
depends_on: [TASK-LN-002]
blocks: [TASK-LN-005, TASK-LN-006]
new_paths:
  - crates/cyberos-luchnham/src/tamtruyen.rs
  - crates/cyberos-luchnham/tests/tamtruyen_oracle.rs
  - crates/cyberos-luchnham/tests/fixtures/tamtruyen_kinliuren.csv
---

## §1 - Description (BCP-14 normative)

This task is the chin tong mon (九宗門), the nine-method decision tree that draws the tam truyen (三傳), the three transmissions - so truyen, trung truyen, mat truyen - from the four lessons. It is the most complex slice of the LiuRen engine and extends the `cyberos-luchnham` crate.

The module SHALL select the so truyen (初傳, initial transmission) by running a single ordered decision tree over the khac/tac census from TASK-LN-002, and SHALL then derive the trung truyen (中傳, middle) and mat truyen (末傳, final) by the tuong nhan chaining: trung truyen is the thien ban chi sitting over the so truyen's palace, mat truyen is the thien ban chi over the trung truyen's palace (Claude-02 s4.1). Once the so truyen is chosen, trung and mat follow automatically; the entire task of the nine methods is to choose the so truyen.

The module SHALL evaluate the tree in this order, taking the first branch whose condition holds (Claude-02 s4.3, s4.4): first phuc ngam (伏吟) when the board state from TASK-LN-001 is `PhucNgam` (nguyet tuong equals gio chiem, offset 0); then phan ngam (返吟) when the board state is `PhanNgam` (nguyet tuong xung gio chiem, offset 6); then, on a normal board, tac khac phap (賊剋) when the census holds exactly one relationship; then ty dung phap (比用) when the census holds two or more and exactly one thuong than is same yin-yang as the day stem; then thiep hai phap (涉害) when ty dung cannot separate them; then, when the census is empty, dao khac (遙剋), mao tinh (昴星), biet trach (別責), and bat chuyen (八專) in that order. This order is normative and MUST NOT be reordered; the special phuc/phan ngam laws MUST be checked before the khac/tac census is even read.

The module SHALL name the resulting khoa the of the method (Nguyen Thu 元首, Trong Tham 重審, Tri Nhat 知一, Thiep Hai 涉害, Cao Thi 蒿矢 or Dan Xa 彈射, Ho Thi Chuyen Bong 虎視轉蓬 or Dong Xa Yem Muc 冬蛇掩目, Biet Trach 別責, Bat Chuyen 八專, Phuc Ngam 伏吟, Phan Ngam 返吟) and emit the tam truyen into `ban.tam_truyen` of the la so envelope (TASK-PLAT-002) under `he = "luc_nham"`, stamping the LN flag set into `co_truong_phai`. The oracle is kinliuren, with dedicated boundary cases for phuc ngam, phan ngam, and bat chuyen.

## §2 - Why this design (rationale for humans)

The nine methods are not nine peers; they are one ordered cascade where only the first satisfied condition fires (Claude-02 s9.1). That single fact is the whole correctness story: many boards satisfy several conditions at once, and reordering the checks silently produces a different, plausible-looking so truyen. The classical enumeration numbers the methods 1..9 with phuc/phan ngam last, but the engine MUST evaluate phuc and phan ngam first, because those two are properties of the board geometry (offsets 0 and 6) that invalidate the ordinary khac/tac reading entirely (Claude-02 s4.3). This task keeps the classical numbering for the lookup table but pins the evaluation order to the s4.4 pseudocode, and the two orders differ on purpose.

The reason this is its own 16-hour slice, larger than its neighbors, is the branch count and the boundary fragility. The vo khac (no-controlling) tail - dao khac, mao tinh, biet trach, bat chuyen - and the two ngam cases are where every LiuRen implementation goes wrong, because they are individually rare and each needs its own hand-built oracle case. Bat chuyen in particular fires only on five specific day pillars (Giap Dan, Dinh Mui, Ky Mui, Canh Than, Quy Suu), so a random-day fixture almost never exercises it and it must be forced in.

There is a real inconsistency in the source that this task resolves rather than inherits: Claude-02 s3.2 and s4.2 define khac (克) as thuong khac ha and tac (賊) as ha khac thuong, and map one khac to Nguyen Thu and one tac to Trong Tham; but the extended lookup table s9.1 (row 1) parenthetically transposes the two labels. The engine follows the method chapters (s3.2, s4.2) and the kinliuren oracle, not the s9.1 parenthetical. This is called out in §9 so a reader of the table does not re-introduce the swap.

## §3 - Contract (algorithm and types)

### The three transmissions and the tuong nhan chain (Claude-02 s4.1)

The so truyen is a chi (a thien ban spirit chosen by the method). Then, reading the thien ban of TASK-LN-001 where `thien_ban[i]` sits over dia ban palace `i`:

- trung truyen = the thien ban chi over the so truyen's dia ban palace.
- mat truyen = the thien ban chi over the trung truyen's dia ban palace.

Example of the chain on the TASK-LN-001 board (offset 11, so `thien_ban` over palace `i` is chi `i - 1`): if the method selects so truyen Suu, then trung truyen is the chi over Suu = Ty, and mat truyen is the chi over Ty = Hoi. The chain is the same for every ordinary method; only the so truyen differs. Phuc ngam and phan ngam replace the chain with hinh/xung laws (below).

### Tac khac phap and the four groups (Claude-02 s4.2, normative)

The census from TASK-LN-002 is the list of `(khoa_index, KhacTac)`. In all ordinary methods the so truyen is a thuong than (upper spirit) of a selected lesson.

- Tac khac phap (賊剋法): the census has exactly one entry. If it is a tac (下剋上), take that lesson's thuong than as so truyen; khoa the = Trong Tham (重審). If it is a khac (上剋下), take that lesson's thuong than as so truyen; khoa the = Nguyen Thu (元首). One khac gives Nguyen Thu, one tac gives Trong Tham (s4.2, s6.2; note the s9.2 table transposes these - follow s4.2).
- Ty dung phap (比用法): the census has two or more entries. Keep the entries whose thuong than is the same yin-yang (am duong) as the day stem (than ty). If exactly one remains, take its thuong than as so truyen; khoa the = Tri Nhat (知一).
- Thiep hai phap (涉害法): two or more entries but ty dung does not leave exactly one (all ty, or all bat ty). Each candidate thuong than returns to its ban gia (home palace) and the number of khac palaces it crosses on the way is counted; the candidate crossing the most khac is the so truyen. On a tie, prefer a candidate on the four manh (Dan Than Ti Hoi), then the four trong (Ty Ngo Mao Dau); khoa the = Thiep Hai (涉害).

### The vo khac tail (Claude-02 s4.2, s4.4 note)

When the census is empty (no khac and no tac in the four khoa), evaluate in order:

- Dao khac (遙剋): a spirit controls the day stem from a distance, or the day stem controls one from a distance. Khoa the = Cao Thi (蒿矢) when a spirit controls the stem, Dan Xa (彈射) when the stem controls a spirit.
- Mao tinh (昴星): the four khoa show four distinct chi. Yang day -> Ho Thi Chuyen Bong (虎視轉蓬); yin day -> Dong Xa Yem Muc (冬蛇掩目), taken by Dau (酉) and the corresponding palace.
- Biet trach (別責): only three distinct chi across the four khoa. Taken by the can hop (stem combination) or chi tam hop.
- Bat chuyen (八專): the day stem and day chi share one palace - the days Giap Dan, Dinh Mui, Ky Mui, Canh Than, Quy Suu - built by the bat chuyen rule.

### Phuc ngam and phan ngam (Claude-02 s4.3)

Checked before everything else, keyed off the `TrangThaiBan` marker set by TASK-LN-001 (do not recompute the offset here):

- Phuc ngam (伏吟): `TrangThaiBan::PhucNgam` (thien ban coincides with dia ban, nothing moved). The tam truyen is built by hinh (刑) and, on self-hinh, by xung (沖): the so truyen seed is the ky cung lesson on a yang day and the day chi on a yin day, then the chain steps by hinh, substituting xung where a spirit would hinh itself (the self-hinh chi Thin Ngo Dau Hoi). Khoa the = Phuc Ngam (伏吟).
- Phan ngam (返吟): `TrangThaiBan::PhanNgam` (thien ban is the dia ban turned six palaces). The tam truyen is built using xung (沖) and hinh (刑). Khoa the = Phan Ngam (返吟).

The exact phuc/phan ngam seed and the self-hinh substitution are pinned to kinliuren (see §9); hinh and xung come from TASK-CORE-007.

### Nine-method lookup table (Claude-02 s9.1, reproduced verbatim)

Classical enumeration order 1..9. The engine's evaluation order is the s4.4 pseudocode below (phuc/phan ngam first); the two orders differ by design.

| Thứ tự | Pháp | Điều kiện áp dụng |
|---|---|---|
| 1 | 賊剋法 Tặc khắc | Có thần trên khắc thần dưới (tặc) hoặc dưới khắc trên (khắc); lấy thần khắc làm sơ truyền |
| 2 | 比用法 Tỷ dụng | Có nhiều chỗ khắc; lấy chỗ khắc cùng âm dương với ngày can làm sơ truyền |
| 3 | 涉害法 Thiệp hại | Nhiều chỗ khắc cùng âm dương; lấy chỗ đi qua nhiều cung khắc hại nhất |
| 4 | 遙剋法 Dao khắc | Không có tặc khắc trực tiếp; lấy thần khắc nhật can từ xa, hoặc nhật can khắc từ xa |
| 5 | 昴星法 Mão tinh | Không tặc khắc, không dao khắc; dùng phép Mão tinh, lấy theo Dậu và cung tương ứng |
| 6 | 別責法 Biệt trách | Ngày không đủ bốn khoá riêng biệt; lấy theo can hợp hoặc chi tam hợp |
| 7 | 八專法 Bát chuyên | Ngày Bát chuyên, can chi cùng một nhà; lập truyền theo phép riêng bát chuyên |
| 8 | 伏吟法 Phục ngâm | Nguyệt tướng gia lên chính thời, thiên địa bàn trùng nhau; lập theo phép phục ngâm |
| 9 | 返吟法 Phản ngâm | Nguyệt tướng đối xung với thời, thiên bàn đối chiếu địa bàn; lập theo phép phản ngâm |

Note on row 1: the parenthetical labels "(tặc)" and "(khắc)" are transposed relative to Claude-02 s3.2 and s4.2. The normative mapping the engine uses is s3.2: thuong khac ha = khac (克) -> Nguyen Thu, ha khac thuong = tac (賊) -> Trong Tham. See §9.

### Pseudocode (Claude-02 s4.4, reproduced verbatim)

```
def lap_tam_truyen(tu_khoa, thien_ban, nguyet_tuong, gio_chiem, can_ngay):
    # Buoc 0: kiem phuc ngam va phan ngam truoc tien
    if nguyet_tuong == gio_chiem:
        return phuc_ngam(tu_khoa, can_ngay)      # 伏吟
    if doi_xung(nguyet_tuong, gio_chiem):
        return phan_ngam(tu_khoa, can_ngay)      # 返吟

    # Buoc 1: liet ke quan he khac (thuong khac ha) va tac (ha khac thuong)
    kc = liet_ke_khac_tac(tu_khoa)   # moi phan tu: (khoa, loai in {KHAC, TAC})

    # Buoc 2: mot khac hoac mot tac -> tac khac phap
    if len(kc) == 1:
        if kc[0].loai == TAC:
            return so_truyen_tu(kc[0], "重審")   # Trong Tham
        else:
            return so_truyen_tu(kc[0], "元首")   # Nguyen Thu

    # Buoc 3: nhieu khac/tac -> ty dung, neu khong phan duoc -> thiep hai
    if len(kc) >= 2:
        ty = [k for k in kc if cung_am_duong(k.thuong_than, can_ngay)]
        if len(ty) == 1:
            return so_truyen_tu(ty[0], "知一")   # Ty dung -> Tri Nhat
        else:
            return thiep_hai(kc, thien_ban)       # 涉害

    # Buoc 4: vo khac vo tac -> bon phep con lai
    if co_dao_khac(tu_khoa, can_ngay):
        return dao_khac(tu_khoa, can_ngay)       # 遙剋: Cao Thi / Dan Xa
    if tu_khoa_du_bon_chi(tu_khoa):
        return mao_tinh(tu_khoa, can_ngay)       # 昴星
    if chi_ba_chi(tu_khoa):
        return biet_trach(tu_khoa, can_ngay)     # 別責
    return bat_chuyen(tu_khoa, can_ngay)         # 八專
```

### Public types (`crates/cyberos-luchnham/src/tamtruyen.rs`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum PhepTruyen {
    TacKhac,    // 賊剋 -> khoa the Nguyen Thu (元首) | Trong Tham (重審)
    TyDung,     // 比用 -> Tri Nhat (知一)
    ThiepHai,   // 涉害
    DaoKhac,    // 遙剋 -> Cao Thi (蒿矢) | Dan Xa (彈射)
    MaoTinh,    // 昴星 -> Ho Thi Chuyen Bong (虎視轉蓬) | Dong Xa Yem Muc (冬蛇掩目)
    BietTrach,  // 別責
    BatChuyen,  // 八專
    PhucNgam,   // 伏吟
    PhanNgam,   // 返吟
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TamTruyen {
    pub so: Chi,                    // sơ truyền (initial)
    pub trung: Chi,                 // trung truyền (middle) = thien ban over so
    pub mat: Chi,                   // mạt truyền (final)  = thien ban over trung
    pub phep: PhepTruyen,           // which of the nine fired
    pub khoa_the_ten: &'static str, // the named khoa the, e.g. "元首", "重審", "知一"
}

pub fn lap_tam_truyen(tu_khoa: &TuKhoa, ban: &ThienDiaBan, can_ngay: Can) -> TamTruyen;
```

## §4 - Acceptance criteria

1. Evaluation order matches the s4.4 pseudocode exactly: phuc ngam and phan ngam are decided from `ban.trang_thai` (TASK-LN-001) before the census is read; a case that is both phuc ngam and would otherwise be a single-khac board resolves as Phuc Ngam.
2. Tac khac phap: a board with exactly one census entry yields Nguyen Thu (元首) when that entry is a khac and Trong Tham (重審) when it is a tac, with the so truyen equal to that lesson's thuong than. Both enumerated.
3. Ty dung / thiep hai split: a two-plus-entry board with exactly one same-yin-yang thuong than yields Tri Nhat (知一); one where ty dung leaves zero or several yields Thiep Hai (涉害) by the crossed-khac count with the manh-before-trong tie-break.
4. Vo khac tail: dedicated cases for dao khac (Cao Thi and Dan Xa), mao tinh (a yang day giving Ho Thi Chuyen Bong and a yin day giving Dong Xa Yem Muc), biet trach (three distinct chi), and bat chuyen (each of the five days Giap Dan, Dinh Mui, Ky Mui, Canh Than, Quy Suu) each fire the correct branch and name.
5. The tuong nhan chain is correct: for every non-ngam result, trung truyen equals the thien ban chi over the so truyen and mat truyen equals the thien ban chi over the trung truyen.
6. Every one of the nine methods has at least one case, and the emitted `ban.tam_truyen` (with `phep` and `khoa_the_ten`) matches kinliuren across the whole fixture; the phuc ngam, phan ngam, and bat chuyen boundary cases match to the digit.

## §5 - Verification

- Unit: one hand-built case per method (nine), plus the five bat chuyen days, plus a self-hinh phuc ngam case, plus a case that is simultaneously phuc ngam and single-khac (must resolve Phuc Ngam), plus the tuong nhan chain property.
- Oracle: `tests/tamtruyen_oracle.rs` loads `fixtures/tamtruyen_kinliuren.csv` (>= 500 cases, generated once from kinliuren and committed) and asserts `so`, `trung`, `mat`, `phep`, and `khoa_the_ten` are identical for every case. The fixture MUST force coverage of all nine methods and all five bat chuyen days, since a random-day sample rarely exercises the vo khac tail.
- Property: for 10,000 random ordinary boards, the tuong nhan chain holds (trung over so, mat over trung) and the fired method is stable under re-evaluation.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-luchnham -- -D warnings`, `cargo test -p cyberos-luchnham`.

## §6 - Implementation skeleton

1. `tamtruyen.rs`: `PhepTruyen`, `TamTruyen` types.
2. `lap_tam_truyen`: implement the s4.4 pseudocode top to bottom - `ban.trang_thai` check first, then the census length branch, then the vo khac tail.
3. `so_truyen_tu`: given the selected lesson's thuong than, derive trung and mat by the tuong nhan chain off `ThienDiaBan`.
4. Helpers: `cung_am_duong` (yin-yang of a chi vs the day stem), `thiep_hai` (crossed-khac count + manh/trong tie-break), `dao_khac`, `mao_tinh`, `biet_trach`, `bat_chuyen`, and `phuc_ngam` / `phan_ngam` (hinh/xung chains via TASK-CORE-007).
5. Emit `TamTruyen` into `ban.tam_truyen` as `{ so, trung, mat, phep }` for `he = "luc_nham"`; carry `khoa_the_ten` for TASK-LN-005; re-stamp the LN flag set.
6. Generate the kinliuren fixture once (documented script, not run in CI), force the nine-method and five-bat-chuyen coverage, and commit; wire the oracle, boundary, and property tests.

## §7 - Dependencies

Depends on TASK-LN-002 (the four lessons and the khac/tac census) and, through it, TASK-LN-001 (the thien ban and the `TrangThaiBan` marker read here). Uses TASK-CORE-007 for ngu hanh, hinh (刑), and xung (沖) relations used by ty dung yin-yang, thiep hai, and the ngam laws. Blocks TASK-LN-005 (khoa the layer 1 is the `khoa_the_ten` this task names) and TASK-LN-006 (assembly). Emits into the TASK-PLAT-002 envelope.

## §8 - Example payloads

`ban.tam_truyen` slice, matching the Claude-02 s8.1 engine JSON field shape (`phep` encodes method and resulting khoa the as `method/khoa_the`):

```json
{ "envelope_version": 1, "he": "luc_nham",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "kien_tung" },
  "lich_phap": { "...": "from TASK-CORE-005" },
  "ban": {
    "thien_dia_ban": { "...": "from TASK-LN-001" },
    "tu_khoa": [ "...": "from TASK-LN-002" ],
    "tam_truyen": { "so": "丑", "trung": "子", "mat": "亥", "phep": "賊克/元首" },
    "thien_tuong": {}
  },
  "cach_cuc": [],
  "co_truong_phai": { "khoi_quy_nhan": "tru_quy", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "..." } }
```

The `phep` string carries the method and the named khoa the (here the illustrative 賊克/元首); TASK-LN-005 promotes that name into `ban.khoa_the` and `cach_cuc`. The `so`/`trung`/`mat` shown are an illustrative chain (Suu -> Ty -> Hoi on the offset-11 board); the fired method and the actual chain for any concrete board are pinned by kinliuren.

## §9 - Open questions

- s9.1 row 1 and s9.2 (TASK-LN-005) transpose the (tac)/(khac) labels and the Nguyen Thu / Trong Tham mapping relative to s3.2 and s4.2. This task follows s3.2/s4.2 (khac = thuong khac ha -> Nguyen Thu; tac = ha khac thuong -> Trong Tham) and the kinliuren oracle. Confirm kinliuren agrees on a single-khac and a single-tac case before locking, and record the decision so the table is not "corrected" back.
- Phuc ngam seed and self-hinh substitution: this task uses the yang-day-ky-cung / yin-day-day-chi seed with xung substituted on self-hinh (Thin Ngo Dau Hoi). Confirm the exact seed and the self-hinh handling against kinliuren; if a school differs, it becomes a flag rather than a hardcode.
- Phan ngam construction (xung then hinh) has minor school variation on the trung/mat step. Default to the kinliuren construction; add a flag only if an oracle case forces it.
- Thiep hai tie-break beyond manh/trong: the four quy (Thin Tuat Suu Mui) ordering is not stated in Claude-02 s4.2. Default to manh, then trong, then quy in canonical index order; confirm on a thiep-hai tie case.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Ngam checked too late | reading the census before the `TrangThaiBan` marker | phuc-ngam-and-single-khac case resolves wrongly; boundary test fails |
| Nguyen Thu / Trong Tham swapped | following the s9.1 parenthetical instead of s4.2 | single-khac and single-tac cases diverge from kinliuren |
| Bat chuyen never exercised | random-day fixture with no bat chuyen day | coverage assertion fails: not all five bat chuyen days present |
| Tuong nhan chain reversed | reading dia ban under the spirit instead of thien ban over the palace | chain property (trung over so) fails |
| Ty dung yin-yang wrong reference | comparing to day chi instead of day stem | Tri Nhat vs Thiep Hai split diverges from oracle |
| Mao tinh day polarity swapped | yang/yin day mapped to the wrong of Ho Thi Chuyen Bong / Dong Xa Yem Muc | mao tinh cases diverge |

## §11 - Notes

This is the hardest LiuRen task and the reason the whole engine is testable: the chin tong mon is a strict ordered cascade, so once each branch has an oracle case the tam truyen is machine-verifiable end to end. Treat the s4.4 pseudocode as the spec of record and the s9.1 table as a lookup whose row-1 parenthetical is known-transposed. The vo khac tail and the two ngam cases carry the boundary risk; their fixtures are forced, not sampled. Oracle kinliuren; the tam truyen match across all nine methods is the core of the TASK-LN-006 100% gate.
