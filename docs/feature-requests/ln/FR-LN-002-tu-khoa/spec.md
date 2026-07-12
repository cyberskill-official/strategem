---
id: FR-LN-002
title: "Tu khoa (four lessons) - khoa 1 from the day stem ky cung and the thien ban chi above it, khoa 2..4 chained through the thien-dia ban overlay, thuong khac ha (克) / ha khac thuong (賊) per ngu hanh; emits tu_khoa into the la so ban for he=luc_nham and stamps co_truong_phai"
module: LN
priority: MUST
status: done
phase: P1
slice: 2
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-02 s3, Grok-29]
related_frs: [FR-LN-001, FR-LN-003, FR-LN-004, FR-LN-006, FR-CORE-007, FR-PLAT-002]
depends_on: [FR-LN-001]
blocks: [FR-LN-003, FR-LN-004, FR-LN-006]
new_paths:
  - crates/cyberos-luchnham/src/tukhoa.rs
  - crates/cyberos-luchnham/tests/tukhoa_oracle.rs
  - crates/cyberos-luchnham/tests/fixtures/tukhoa_kinliuren.csv
---

## §1 - Description (BCP-14 normative)

This FR builds the tu khoa (四課), the four lessons that every LiuRen chart reads off the rotated thien ban. It extends the `cyberos-luchnham` crate born in FR-LN-001; it adds no new crate.

The module SHALL construct four columns from the day stem and the day chi, each column a ha than (下神, lower spirit) below and a thuong than (上神, upper spirit) above, using the thien ban produced by FR-LN-001. The four are built in a fixed chained order (Claude-02 s3.1): khoa 1 takes the day stem's ky cung palace as ha than and the thien ban chi sitting over that palace as thuong than; khoa 2 takes khoa 1's thuong than, locates it on the dia ban, and reads the thien ban chi over it as the new thuong than; khoa 3 takes the day chi as ha than and the thien ban chi over it as thuong than; khoa 4 takes khoa 3's thuong than as ha than and the thien ban chi over it as thuong than. The reading order is right to left, khoa 1 outermost right.

The module SHALL classify, for each of the four khoa, the ngu hanh relationship between thuong than and ha than into exactly one of: thuong khac ha (上剋下), the upper controls the lower, named khac (克); ha khac thuong (下剋上), the lower controls the upper, named tac (賊); or neither. The relationship SHALL be computed by ngu hanh sinh khac (FR-CORE-007) on the elements of the two spirits. This khac/tac census over the four khoa is the sole input to the nine-method decision tree in FR-LN-003; this FR produces the census, FR-LN-003 consumes it.

For khoa 1 the ha than stands for the day stem, not the parked branch: the module SHALL use the day stem's own element (Can -> NguHanh) as the lower element in khoa 1's khac test, even though the ha than is seated at the ky cung palace. This matters because a stem and its ky cung branch can differ in element (for example Mau 戊 is Tho but its ky cung Ti 巳 is Hoa), and the classical census and the kinliuren oracle key off the stem element.

The module SHALL emit the four khoa into `ban.tu_khoa` of the la so envelope (FR-PLAT-002) under `he = "luc_nham"`, and SHALL re-stamp the LN flag set (khoi_quy_nhan, truong_sinh_phai) into `co_truong_phai` unchanged from FR-LN-001, since this slice branches on none of them. The oracle is kinliuren.

## §2 - Why this design (rationale for humans)

The four lessons are the hinge between the board and the chart. FR-LN-001 turned time into a rotated thien ban; the tu khoa turn that board into the four upper/lower pairs from which the three truyen are drawn. Everything FR-LN-003 does is decide which of the four columns supplies the so truyen, and that decision is made purely from the khac/tac census this FR emits, so the census must be exactly right or the whole tam truyen is wrong while still looking plausible (Claude-02 s1.2, the propagation warning).

The chained construction (each even lesson built from the odd lesson's upper) is what makes the four lessons interlock rather than be four independent lookups. It is fully deterministic - four reads off the thien ban plus one ky cung lookup - so it is pure data with no school branch, which is why it is a small slice that exists mainly to get the khac/tac direction and the khoa-1 stem-element rule pinned before the hard FR-LN-003 lands.

The khoa-1 stem-element point is the silent bug of this slice. It is tempting to treat khoa 1's lower as just another chi (the ky cung branch) and compare branch elements, and for a stem like Giap 甲 whose ky cung is Dan 寅 (both Moc) nothing breaks, so a test suite built only on Giap-like days passes. The bug only surfaces on Mau, Ky, Binh days where the stem and its ky cung diverge in element, so the acceptance criteria force a day of that kind into the fixture.

## §3 - Contract (algorithm and types)

### Building the four lessons (Claude-02 s3.1, reproduced)

Read the thien ban as: `thien_ban[i]` is the chi sitting over dia ban palace `i` (FR-LN-001). Let `ky_cung(can)` be the ky cung palace of the day stem (FR-LN-001) and `chi_ngay` the day chi.

1. Khoa 1: ha than = day stem at its ky cung palace; thuong than = the thien ban chi over that palace.
2. Khoa 2: ha than = khoa 1's thuong than; find that chi's own dia ban palace; thuong than = the thien ban chi over it.
3. Khoa 3: ha than = day chi; thuong than = the thien ban chi over the day chi's palace.
4. Khoa 4: ha than = khoa 3's thuong than; thuong than = the thien ban chi over that chi's palace.

Each even lesson is thus the odd lesson's upper "climbed once more" up the thien ban. The four are indexed 1..4 but stored 0..3; khoa 1 is the rightmost when drawn.

### Thuong khac ha and ha khac thuong (Claude-02 s3.2, normative)

For each khoa, take the element of the thuong than and the element of the ha than (for khoa 1 the ha than element is the day stem's element, per §1) and apply ngu hanh khac (FR-CORE-007, the controlling cycle Moc -> Tho -> Thuy -> Hoa -> Kim -> Moc):

- thuong khac ha (上剋下), upper controls lower: named khac (克).
- ha khac thuong (下剋上), lower controls upper: named tac (賊).
- neither controls the other (same element, or the sinh direction): no relationship.

The full census over the four khoa - the list of `(khoa_index, KhacTac)` - is this FR's headline output and the input to FR-LN-003. Sinh (generating) and same-element pairs contribute nothing to the census; only khac and tac count.

### Worked example (Claude-02 s3.3, reproduced)

Nguyet tuong Hoi, gio Ty, day Giap Ty. Gia nguyet tuong (FR-LN-001) puts Hoi over the Ty palace, giving offset 11, so over Dan sits Suu, over Suu sits Ty, over Ty sits Hoi, over Hoi sits Tuat. Day stem Giap ky cung Dan. Reading right to left:

| Khoá | Hạ thần | Thượng thần | Nguồn hạ thần |
|---|---|---|---|
| Khoá 1 | 甲 (寄寅) | 丑 | Can Giáp ký cung Dần |
| Khoá 2 | 丑 | 子 | Thượng thần khoá 1 |
| Khoá 3 | 子 | 亥 | Chi ngày Tý |
| Khoá 4 | 亥 | 戌 | Thượng thần khoá 3 |

So the four lessons are Suu over Giap, Ty over Suu, Hoi over Ty, Tuat over Hoi. The khac/tac census on this board (elements: Suu 丑 Tho, Ty 子 Thuy, Hoi 亥 Thuy, Tuat 戌 Tho; day stem Giap 甲 Moc):

- Khoa 1: thuong Suu (Tho), ha Giap (Moc). Moc khac Tho, so the lower controls the upper -> tac (賊).
- Khoa 2: thuong Ty (Thuy), ha Suu (Tho). Tho khac Thuy, lower controls upper -> tac (賊).
- Khoa 3: thuong Hoi (Thuy), ha Ty (Thuy). same element -> none.
- Khoa 4: thuong Tuat (Tho), ha Hoi (Thuy). Tho khac Thuy, upper controls lower -> khac (克).

The census is thus {khoa1: tac, khoa2: tac, khoa4: khac}, three relationships. Because there is more than one, FR-LN-003 will not use the single-relationship tac khac phap; it will fall through to ty dung or thiep hai. This FR stops at the census; it does not select the so truyen. Note khoa 1 uses Giap = Moc; the ky cung Dan is also Moc, so this example is stem/branch-robust, which is exactly why the fixture must also carry a Mau or Ky day.

### Public types (`crates/cyberos-luchnham/src/tukhoa.rs`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum KhacTac { KhacThuongHa, TacHaThuong }   // 克 upper controls lower | 賊 lower controls upper

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Khoa {
    pub thuong_than: Chi,          // upper spirit (always a chi)
    pub ha_than: Chi,              // lower spirit (khoa 1 = the day stem's ky cung palace)
    pub la_can_khoa: bool,         // true only for khoa 1: ha than stands for the day stem
    pub quan_he: Option<KhacTac>,  // None when neither controls
}

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct TuKhoa {
    pub khoa: [Khoa; 4],           // index 0 = khoa 1 (rightmost), .. index 3 = khoa 4
}

pub fn lap_tu_khoa(ban: &ThienDiaBan, can_ngay: Can, chi_ngay: Chi) -> TuKhoa;
pub fn quan_he_khoa(thuong: NguHanh, ha: NguHanh) -> Option<KhacTac>;   // ngu hanh census unit
pub fn census_khac_tac(tk: &TuKhoa) -> Vec<(usize, KhacTac)>;            // input to FR-LN-003
```

## §4 - Acceptance criteria

1. `lap_tu_khoa` reproduces the Claude-02 s3.3 worked example exactly: the four `(thuong_than, ha_than)` pairs are (Suu, Giap-at-Dan), (Ty, Suu), (Hoi, Ty), (Tuat, Hoi), and the value matches kinliuren.
2. The chained construction holds structurally: khoa 2's ha than equals khoa 1's thuong than and khoa 4's ha than equals khoa 3's thuong than, for all sampled boards.
3. The khac/tac census on the s3.3 board is exactly {khoa1: TacHaThuong, khoa2: TacHaThuong, khoa4: KhacThuongHa}, khoa3 None.
4. Khoa-1 stem-element rule: for a Mau or Ky day (stem element differs from ky cung branch element), the khoa-1 census uses the stem element; an enumerated test on a Mau day diverges from the branch-element computation and agrees with kinliuren.
5. `quan_he_khoa` is correct over all 25 ordered element pairs (khac, tac, or none) against the FR-CORE-007 khac cycle.
6. The emitted `ban.tu_khoa` round-trips through the la so envelope (FR-PLAT-002) under `he = "luc_nham"` as the `[thuong_than, ha_than]` pair array (see §8), and `co_truong_phai` still carries the LN flag set unchanged from FR-LN-001.

## §5 - Verification

- Unit: the s3.3 worked example (four pairs + census); the chained-construction structural property over sampled boards; `quan_he_khoa` over all 25 element pairs; the Mau/Ky khoa-1 stem-element case.
- Oracle: `tests/tukhoa_oracle.rs` loads `fixtures/tukhoa_kinliuren.csv` (>= 500 cases spanning day stem x day chi x board offset, generated once from kinliuren and committed) and asserts the four lessons and the khac/tac census are identical for every case. The fixture MUST include at least one day per stem, so Mau/Ky/Binh divergence days are covered.
- Property: for 10,000 random (board, day stem, day chi) triples, khoa 2's ha than equals khoa 1's thuong than and khoa 4's ha than equals khoa 3's thuong than; every thuong than is a valid thien ban chi of the given board.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-luchnham -- -D warnings`, `cargo test -p cyberos-luchnham`.

## §6 - Implementation skeleton

1. `tukhoa.rs`: `KhacTac`, `Khoa`, `TuKhoa` types.
2. `lap_tu_khoa`: the four chained reads off `ThienDiaBan` (FR-LN-001) plus the `ky_cung` lookup for khoa 1.
3. `quan_he_khoa`: ngu hanh khac census unit, taking two `NguHanh` (FR-CORE-007 provides `hanh_of_chi` and `hanh_of_can`); wire khoa 1 to `hanh_of_can(can_ngay)`.
4. `census_khac_tac`: fold over the four khoa, dropping `None`.
5. Emit `TuKhoa` into `ban.tu_khoa` as the `[thuong_than, ha_than]` array for `he = "luc_nham"`; re-stamp the LN flag set unchanged.
6. Generate the kinliuren fixture once (documented script, not run in CI), ensuring one day per stem, and commit; wire the oracle and property tests.

## §7 - Dependencies

Depends on FR-LN-001 (the thien ban, the `Chi`/`Can` primitives, the ky cung table, and the envelope wiring). Uses FR-CORE-007 for ngu hanh sinh khac and the chi/can element lookups (`hanh_of_chi`, `hanh_of_can`); if CORE-007 is not yet `done`, a local element table may be inlined and later replaced, but the khac cycle MUST match CORE-007 exactly. Blocks FR-LN-003 (the nine-method tree consumes the khac/tac census), FR-LN-004 (sequenced after this slice in the same crate), and FR-LN-006 (assembly). Emits into the FR-PLAT-002 envelope.

## §8 - Example payloads

Worked example, day Giap Ty, gio Ty, nguyet tuong Hoi. The envelope's `ban.tu_khoa` uses the `[thuong_than, ha_than]` pair order (upper first), matching the engine JSON in Claude-02 s8.1:

```json
{ "envelope_version": 1, "he": "luc_nham",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "hon_nhan" },
  "lich_phap": { "...": "from FR-CORE-005" },
  "ban": {
    "thien_dia_ban": { "...": "from FR-LN-001" },
    "tu_khoa": [ ["丑","甲"], ["子","丑"], ["亥","子"], ["戌","亥"] ],
    "tam_truyen": {}, "thien_tuong": {}
  },
  "cach_cuc": [],
  "co_truong_phai": { "khoi_quy_nhan": "tru_quy", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "..." } }
```

Reading the array: khoa 1 is `["丑","甲"]` = thuong than Suu over ha than Giap (seated at ky cung Dan); khoa 3 is `["亥","子"]` = thuong than Hoi over ha than Ty (the day chi). Beware the two orders in play: the s3.3 table lists ha than then thuong than; the JSON array lists thuong than then ha than. The census {khoa1 tac, khoa2 tac, khoa4 khac} is carried in-engine for FR-LN-003 and is not part of the emitted `ban.tu_khoa` array.

## §9 - Open questions

- Khoa-1 lower element: this FR fixes it to the day stem's element (per classical census and kinliuren), not the ky cung branch's element. Claude-02 s3.2 phrases the khac test as "hanh cua hai chi" (elements of the two branches), which reads as the branch element; the two agree for Giap/At-like stems and diverge for Mau/Ky/Binh. Confirm against kinliuren on a Mau day before locking; the fixture requirement in §5 forces this.
- Does any school count a sinh (generating) relationship in the four-khoa census? Default: no - only khac and tac enter the census (Claude-02 s3.2, s4). Confirm no oracle case depends on a sinh entry.
- Pair order in the emitted array is `[thuong_than, ha_than]` to match Claude-02 s8.1. Confirm FR-LN-006 and CHART-002 read the same order so the drawn board and the array never disagree.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Khoa-1 uses branch element | comparing ky cung branch element instead of the stem element | Mau-day enumerated test diverges from kinliuren; do not ship |
| Chain broken | khoa 2/4 not built from the preceding upper | structural property (khoa2.ha == khoa1.thuong) fails |
| Khac/tac direction reversed | thuong khac ha vs ha khac thuong swapped | s3.3 census (khoa1 tac, khoa4 khac) diverges; oracle fails |
| Sinh counted as a relationship | census includes generating pairs | property test finds a non-khac/tac entry; census size wrong |
| Pair order flipped in JSON | emitting `[ha, thuong]` | envelope round-trip vs s8.1 golden diverges; CHART-002 mis-draws |

## §11 - Notes

The tu khoa are deliberately a thin, pure slice whose real product is the khac/tac census - the single argument the nine-method tree in FR-LN-003 runs on. Getting the census direction and the khoa-1 stem-element rule exactly right here is what keeps FR-LN-003 honest, so the fixture is required to span every day stem rather than a convenient handful. This FR introduces no school flag; it re-stamps FR-LN-001's set unchanged so a chart is still reproducible from its stamp. Oracle kinliuren; this tu khoa oracle is one more calendar-independent half of the FR-LN-006 100% gate.
