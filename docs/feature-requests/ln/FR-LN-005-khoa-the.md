---
id: FR-LN-005
title: "Khoa the + luc than + dung than - named chart-body patterns (課體) as predicates over the assembled board, luc than by ngu hanh vs the day stem, dung than by question type; emits khoa_the/luc_than into the la so ban and cach_cuc for he=luc_nham"
module: LN
priority: SHOULD
status: ready_to_implement
phase: P1
slice: 5
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-02 s6, Claude-02 s9.2, Grok-29]
related_frs: [FR-LN-003, FR-LN-004, FR-LN-006, FR-CORE-004, FR-CORE-007, FR-RULE-002, FR-PLAT-002]
depends_on: [FR-LN-003, FR-LN-004]
blocks: []
new_paths:
  - crates/cyberos-luchnham/src/khoathe.rs
  - crates/cyberos-luchnham/src/lucthan.rs
  - crates/cyberos-luchnham/tests/khoathe_oracle.rs
  - crates/cyberos-luchnham/tests/fixtures/khoathe_cases.csv
---

## §1 - Description (BCP-14 normative)

This FR adds the interpretation-facing layer of the LiuRen chart: khoa the (課體, named chart-body patterns), luc than (六親, the six kinships), and dung than (用神, the useful spirit chosen by question type). It extends the `cyberos-luchnham` crate. It is SHOULD, not MUST: FR-LN-006 can assemble and pass its oracle gate without this layer, and this FR enriches the assembled board.

The module SHALL recognize khoa the as a set of predicates over the fully assembled board (four khoa, three truyen, twelve generals). Recognition SHALL span two layers (Claude-02 s6.1): layer one is the khoa the tied directly to the tam truyen method (Nguyen Thu, Trong Tham, Tri Nhat, Thiep Hai, Mao Tinh, Biet Trach, Bat Chuyen, Phuc Ngam, Phan Ngam), read straight off FR-LN-003's `PhepTruyen` and `khoa_the_ten`; layer two is the khoa the recognized from the overall shape of the board (Tam Quang, Tam Duong, Long Duc, Chu An, Tram Quan, Be Khau, Du Tu, and the rest), each a predicate over the four khoa, three truyen, generals, and than sat. The module SHALL recognize every khoa the a board matches, because one board can carry several at once, and SHALL NOT stop at the first match.

The module SHALL assign luc than to a chi by the ngu hanh relationship between that chi and the day stem (FR-CORE-007): the element that generates the day stem is Phu Mau, the element the day stem generates is Tu Ton, the element that controls the day stem is Quan Quy, the element the day stem controls is The Tai, the same element is Huynh De (Claude-02 s6.3). The module SHALL select the dung than for a chart from `dau_vao.loai_cau_hoi` via the luc than mapping (tai loc -> The Tai, cong danh -> Quan Quy, con cai -> Tu Ton, cha me / nha cua -> Phu Mau), returning the chi (or chart position) that carries that luc than.

The module SHALL emit the recognized khoa the into both `ban.khoa_the` (the LiuRen-native name list) and the cross-engine `cach_cuc` array of the la so envelope (FR-PLAT-002, each entry with id, name, polarity, citations), emit luc than into `ban.luc_than` and the chosen dung than into `ban.dung_than`, all under `he = "luc_nham"`, and stamp the LN flag set. The truong_sinh_phai flag (FR-LN-001) governs the vuong/suy assessment a downstream reader applies to the dung than. This layer has no numeric oracle of its own; its predicates are cross-checked against Luc Nham Dai Toan and Tat phap phu (Claude-02 s6.2) plus kinliuren where the method-tied khoa the overlap.

## §2 - Why this design (rationale for humans)

Khoa the is where a LiuRen chart stops being a lattice of spirits and becomes a readable situation. The classical corpus names roughly sixty-four chart bodies, each a compact diagnosis ("this shape means the matter passes through obstacles before it resolves"), and recognizing them is exactly a rule engine: a list of predicates evaluated over the assembled board (Claude-02 s6.1). Framing it as predicates - not as a free-text label the AI invents - keeps it on the deterministic side of the platform boundary and lets FR-RULE-002's condition DSL and the interpretation layer consume named, cited patterns rather than guesses (strategy 4.3, 4.4).

Two layers exist because two kinds of khoa the exist. The method-tied ones are already decided the moment FR-LN-003 picks a method - Nguyen Thu is nothing more than "the single-khac tac khac result" - so they cost nothing to surface. The shape-based ones (Tam Quang, Long Duc, and the rest) are genuine predicates over the whole board and generals, and they overlap, so a board legitimately carries several names at once; the design recognizes all of them and lets the interpretation layer pick which to lead with. Nguyen Thu alone matches a large share of boards (about 115 of 720 yang-day charts per Claude-02 s6.2), so "recognize all, rank later" is the only sound rule.

Luc than and dung than are the mechanism that points the whole chart at the actual question. Luc than classifies every spirit relative to the querent (the day stem); dung than picks the one spirit that stands for what was asked. Without dung than the chart is a general weather report; with it, the reader knows which spirit's state - which lesson, which truyen, which general it rides, vuong or suy, void or intact - is the answer (Claude-02 s6.3, s7). Because luc than is pure ngu hanh against the day stem, it reuses FR-CORE-007 rather than re-deriving relations.

## §3 - Contract (algorithm and types)

### Khoa the, two layers (Claude-02 s6.1, s6.2, reproduced)

Layer one is read from FR-LN-003. Layer two is predicate recognition. Main named chart bodies (Claude-02 s6.2):

| Khoá thể | Điều kiện nhận (rút gọn) | Hướng đoán |
|---|---|---|
| 元首 Nguyên Thủ | Một thượng khắc hạ, dùng khắc làm sơ | Việc thuận theo lẽ chính, đầu mối rõ |
| 重審 Trọng Thẩm | Một hạ khắc thượng, dùng tặc làm sơ | Việc do dưới phát, nên xét kỹ lại |
| 知一 Tri Nhất | Nhiều khắc, chọn tỷ làm sơ | Nhiều lối, chọn bên gần mình |
| 涉害 Thiệp Hại | Nhiều khắc đều tỷ hoặc đều bất tỷ | Việc nhiều trở ngại, lội qua hại |
| 三光 Tam Quang | Ba truyền và can chi đều vượng cát | Việc sáng sủa, nhiều thuận lợi |
| 三陽 Tam Dương | Cách cục dương khí thịnh | Hướng lên, tiến tới tốt |
| 龍德 Long Đức | Thanh long thừa thần cát | Có phúc trợ, hỷ sự |
| 鑄印 Chú Ấn | Cách ấn thụ thành tựu | Nhậm chức, được ấn tín, danh vị |
| 斬關 Trảm Quan | Có chi chủ vượt ải | Vượt trở ngại, xuất hành gấp |
| 閉口 Bế Khẩu | Cách khẩu bị bịt | Việc khó nói, bế tắc thông tin |
| 遊子 Du Tử | Cách người đi xa | Đi xa, xa cách, phiêu bạt |

Extended named list (Claude-02 s9.2, reproduced verbatim):

| Khoá thể | Điều kiện định nghĩa |
|---|---|
| 元首課 Nguyên thủ | Chỉ một chỗ khắc, dưới khắc trên, lấy làm sơ truyền; khoá thuần và thuận |
| 重審課 Trọng thẩm | Chỉ một chỗ khắc, trên khắc dưới (tặc); cần xét kỹ, việc có trở lực |
| 知一課 Tri nhất | Nhiều chỗ khắc, dùng tỷ dụng lấy một chỗ cùng âm dương; chọn một mối chính |
| 涉害課 Thiệp hại | Lập truyền theo thiệp hại; việc qua nhiều trở ngại mới thành |
| 遙剋課 Dao khắc | Lập truyền theo dao khắc; tác động từ xa, gián tiếp |
| 昴星課 Mão tinh | Lập truyền theo Mão tinh; cuộc hỏi bất định, cần nương phép riêng |
| 別責課 Biệt trách | Khoá không đủ bốn, lập theo biệt trách; việc thiếu đầu mối rõ |
| 八專課 Bát chuyên | Ngày bát chuyên can chi cùng nhà; việc trong ngoài lẫn, khó phân |
| 伏吟課 Phục ngâm | Thiên địa bàn trùng; việc ngưng trệ, ẩn phục, chưa động |
| 返吟課 Phản ngâm | Thiên bàn đối xung địa bàn; việc đảo lộn, phản phục, đổi chiều |
| 三光課 Tam quang | Ba truyền đều gặp cát tướng cát thần; cuộc sáng sủa, thuận lợi |
| 三陽課 Tam dương | Ba truyền theo thế dương tiến; việc hướng lên, phát triển |

Reconciliation note: the s9.2 rows for Nguyen thu ("duoi khac tren") and Trong tham ("tren khac duoi (tac)") are transposed relative to s6.2 and to s4.2. The engine uses the s4.2 / s6.2 mapping (Nguyen Thu = thuong khac ha = khac 克; Trong Tham = ha khac thuong = tac 賊), consistent with FR-LN-003. The s9.2 table is reproduced here as-is for completeness; do not wire recognition from its transposed parentheticals.

### Luc than by ngu hanh vs the day stem (Claude-02 s6.3, reproduced)

| Quan hệ với ta | Lục thân | Loại việc và người tiêu biểu |
|---|---|---|
| Sinh ra ta | 父母 Phụ mẫu | Cha mẹ, bề trên, nhà cửa, giấy tờ, chỗ dựa |
| Ta sinh ra | 子孫 Tử tôn | Con cháu, cấp dưới, phúc lộc, giải cứu |
| Khắc ta | 官鬼 Quan quỷ | Quan chức, chồng, bệnh tật, mối lo, đối thủ |
| Ta khắc | 妻財 Thê tài | Vợ, tiền của, tài sản, thứ mình nắm |
| Cùng hành với ta | 兄弟 Huynh đệ | Anh em, đồng nghiệp, đối tác ngang, cạnh tranh |

"Ta" is the day stem's element (FR-CORE-007). Dung than by question type: tai loc -> The Tai, cong danh -> Quan Quy, con cai -> Tu Ton, cha me / nha cua -> Phu Mau (Claude-02 s6.3). After selection, the reader examines the dung than's state - its lesson, its truyen, the general it rides, vuong or suy (truong_sinh_phai), void (tuan khong from FR-CORE-004), hinh/xung (FR-CORE-007).

### Public types (`crates/cyberos-luchnham/src/khoathe.rs`, `lucthan.rs`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum LucThan { PhuMau, TuTon, QuanQuy, TheTai, HuynhDe }   // 父母 子孫 官鬼 妻財 兄弟

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum KhoaTheLayer { TamTruyen, HinhThai }                  // method-tied | shape-based

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct KhoaThe {
    pub id: String,             // e.g. "nguyen_thu", "tam_quang"
    pub han: &'static str,      // 元首, 三光
    pub layer: KhoaTheLayer,
    pub polarity: Polarity,     // Cat | Hung | Trung (envelope enum)
    pub citations: Vec<String>, // Luc Nham Dai Toan / Tat phap phu references
}

pub fn luc_than_cua(chi: Chi, can_ngay: Can) -> LucThan;
pub fn dung_than(loai_cau_hoi: LoaiCauHoi) -> LucThan;
pub fn nhan_dien_khoa_the(ban: &BanLucNham) -> Vec<KhoaThe>;   // all matches, not the first
```

## §4 - Acceptance criteria

1. Layer-one khoa the are surfaced directly from FR-LN-003: a board whose method is TacKhac/khac carries Nguyen Thu (元首), a bat chuyen board carries Bat Chuyen (八專), a phuc ngam board carries Phuc Ngam (伏吟), each with the FR-LN-003 name.
2. `nhan_dien_khoa_the` returns all matching khoa the, not the first: a board matching both Nguyen Thu and Tam Quang returns both.
3. Nguyen Thu / Trong Tham are recognized by the s4.2 / s6.2 mapping (khac -> Nguyen Thu, tac -> Trong Tham), not the transposed s9.2 parenthetical; an enumerated test asserts the correct direction.
4. `luc_than_cua` is correct for all five relationships against the FR-CORE-007 sinh/khac cycle relative to the day stem, verified across several day stems.
5. `dung_than` maps each supported `loai_cau_hoi` to the correct luc than, and the returned dung than is the chart position carrying that luc than.
6. The emitted `ban.khoa_the`, `ban.luc_than`, `ban.dung_than`, and the `cach_cuc` entries round-trip through the la so envelope (FR-PLAT-002) under `he = "luc_nham"`; each `cach_cuc` entry carries id, name, polarity, and at least one citation; `co_truong_phai` carries the LN flag set including truong_sinh_phai.

## §5 - Verification

- Unit: layer-one surfacing for Nguyen Thu, Bat Chuyen, Phuc Ngam; the "recognize all" property on a multi-match board; the Nguyen Thu / Trong Tham direction test; `luc_than_cua` over five relationships x several day stems; `dung_than` over each supported question type.
- Predicate cross-check: `tests/khoathe_oracle.rs` loads `fixtures/khoathe_cases.csv` (hand-curated boards with expected khoa the and citations, drawn from Luc Nham Dai Toan and Tat phap phu, and cross-checked with kinliuren where the method-tied khoa the overlap) and asserts the recognized set equals the expected set for each case.
- Consistency: for every board in the FR-LN-003 fixture, the layer-one khoa the recognized here equals the `khoa_the_ten` FR-LN-003 emitted (no drift between the two slices).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-luchnham -- -D warnings`, `cargo test -p cyberos-luchnham`.

## §6 - Implementation skeleton

1. `lucthan.rs`: `LucThan`, `luc_than_cua` (ngu hanh vs day stem via FR-CORE-007), `dung_than` (question-type map).
2. `khoathe.rs`: `KhoaThe`, `KhoaTheLayer`; layer-one surfacing from FR-LN-003's `PhepTruyen` / `khoa_the_ten`.
3. Layer-two predicates as a table of named rules over `BanLucNham` (four khoa, three truyen, generals); model them so FR-RULE-002's condition DSL can later express them.
4. `nhan_dien_khoa_the`: evaluate all predicates, collect every match.
5. Emit khoa the into `ban.khoa_the` (name list) and `cach_cuc` (id/name/polarity/citations); emit luc than into `ban.luc_than` and dung than into `ban.dung_than`; stamp the LN flag set.
6. Curate `khoathe_cases.csv` from the cited classical sources; wire the predicate cross-check and the FR-LN-003 consistency test.

## §7 - Dependencies

Depends on FR-LN-003 (method-tied khoa the and the truyen) and FR-LN-004 (the generals that shape-based khoa the read). Uses FR-CORE-007 for luc than ngu hanh and hinh/xung, and FR-CORE-004 for tuan khong and vuong/suy used in dung than state assessment. Models predicates so FR-RULE-002 can consume them. Does not block any FR (FR-LN-006 is MUST and does not depend on this SHOULD layer); FR-LN-006 emits layer-one khoa the from FR-LN-003 even when this slice is absent, and this slice enriches `ban.khoa_the`, `ban.luc_than`, `ban.dung_than`, and `cach_cuc`. Emits into the FR-PLAT-002 envelope.

## §8 - Example payloads

`ban.khoa_the` / `luc_than` / `dung_than` and the `cach_cuc` promotion:

```json
{ "envelope_version": 1, "he": "luc_nham",
  "dau_vao": { "datetime": "...", "tz": "+07:00", "kinh_do": 106.7, "loai_cau_hoi": "tai_loc" },
  "lich_phap": { "...": "from FR-CORE-005" },
  "ban": {
    "thien_dia_ban": { "...": "from FR-LN-001" },
    "tu_khoa": [ "...": "from FR-LN-002" ],
    "tam_truyen": { "...": "from FR-LN-003" },
    "thien_tuong": { "...": "from FR-LN-004" },
    "khoa_the": ["元首", "三光"],
    "luc_than": [ { "chi": "亥", "luc_than": "妻財" }, { "chi": "丑", "luc_than": "官鬼" } ],
    "dung_than": { "loai_cau_hoi": "tai_loc", "luc_than": "妻財", "chi": "亥" }
  },
  "cach_cuc": [
    { "id": "nguyen_thu", "name": "元首", "cung": null, "polarity": "cat", "score": null, "citations": ["Luc Nham Dai Toan"] },
    { "id": "tam_quang", "name": "三光", "cung": null, "polarity": "cat", "score": null, "citations": ["Tat phap phu"] }
  ],
  "co_truong_phai": { "khoi_quy_nhan": "tru_quy", "quy_nhan_variant": "giap_mau_canh", "truong_sinh_phai": "ngu_hanh" },
  "provenance": { "engine": "ln", "engine_version": "0.1.0", "cast_at": "..." } }
```

The board here carries two khoa the at once (Nguyen Thu and Tam Quang), both promoted into `cach_cuc` with citations. The dung than for a tai_loc question is the The Tai spirit (here Hoi); the interpretation layer reads that spirit's state to answer.

## §9 - Open questions

- Full khoa the coverage: Claude-02 s6.2 says roughly sixty-four chart bodies exist; this FR ships the s6.2 and s9.2 named set and a predicate table designed to grow. Decide whether the full sixty-four are in scope for P1 or deferred to a KB-seeded expansion (FR-KB-002), keeping the recognizer data-driven either way.
- Nguyen Thu / Trong Tham source conflict: resolved in favor of s4.2 / s6.2 over the transposed s9.2. Confirm once against kinliuren and record, mirroring the FR-LN-003 decision.
- Dung than granularity: some questions map to more than one luc than (a marriage question touches The Tai and Quan Quy). Default to a primary luc than per question type; revisit a multi-dung-than return with FR-STRAT-003 (the chu-khach framework).
- Should the shape-based predicates live here or move to FR-RULE-002 once its DSL exists? Default: define them here as data so RULE can later evaluate them; avoid duplicating the logic.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| First-match only | returning the first khoa the instead of all | multi-match board test finds a missing name |
| s9.2 transposition wired | recognizing Nguyen Thu as "duoi khac tren" | direction test diverges from s4.2 / FR-LN-003 |
| Luc than reference wrong | classifying vs the day chi instead of the day stem | `luc_than_cua` diverges across day stems |
| Layer drift | layer-one khoa the disagree with FR-LN-003 | the consistency test against the FR-LN-003 fixture fails |
| Uncited cach_cuc | promoting a khoa the with no citation | envelope check rejects a `cach_cuc` entry lacking citations |

## §11 - Notes

This SHOULD slice is the bridge from the deterministic LiuRen board to the cited interpretation layer: khoa the become `cach_cuc` patterns, luc than and dung than point the chart at the question, and all of it stays predicate-and-citation based so nothing here is an AI guess (strategy 4.3). It deliberately does not gate FR-LN-006 - the engine ships its oracle-exact board without this enrichment - which is why it is SHOULD while its neighbors are MUST. The predicate table is authored as data so FR-RULE-002 and the KB can grow it toward the full classical sixty-four without touching engine code. The s9.2 transposition is reproduced but not wired; the engine follows s4.2 / s6.2 and kinliuren.
