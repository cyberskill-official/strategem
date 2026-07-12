---
id: FR-QMDG-007
title: "Dung than by question type - the QiMen dung than selection table (Claude-03 s7.3) as data: given a question type, select the dung than and locate each on the assembled chart; selecting + locating is deterministic, reading its palace is the cited AI layer"
module: QMDG
priority: SHOULD
status: ready_to_implement
phase: P1
slice: 1
lang: rust
effort_h: 6
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.3, strategy 7, Claude-03 s7.3, Claude-03 s7]
related_frs: [FR-QMDG-006, FR-PLAT-002, FR-CORE-005, FR-RAG-003, FR-STRAT-003]
depends_on: [FR-QMDG-006]
blocks: []
new_paths:
  - crates/cyberos-qimen/src/dung_than.rs
  - crates/cyberos-qimen/tests/dung_than.rs
  - crates/cyberos-qimen/tests/fixtures/dung_than_cases.json
---

## §1 - Description (BCP-14 normative)

This FR adds the QiMen dung than (用神) selection by question type: given a `loai_cau_hoi` and an assembled QiMen chart (the FR-QMDG-006 la so, `he = "ky_mon"`), it selects the dung than for that question and locates each on the chart. It reproduces the mapping table in Claude-03 s7.3 as data.

The module SHALL encode the s7.3 table as a static, reviewable selection map from `LoaiCauHoi` to a list of `(vai, ky_hieu)` pairs - a role (self, wealth, opponent, matchmaker, ...) and the chart symbol that stands for it (a can, a mon, a sao, a than, a direction, or dich ma). For an assembled chart the module SHALL resolve each selected symbol to the palace (cung, 1..=9) it occupies on that chart, reading the la so `ban` (and, for the day / hour stems and dich ma, the `lich_phap` context from FR-CORE-005). The entry point `dung_than(loai, &LaSo)` SHALL return the selected, located dung than.

The selection and the location SHALL be deterministic facts: selecting the dung than is a fixed convention (s7.3), and locating a symbol on a completed chart is a lookup, so both are engine-owned. Reading what the located palace means for the question - through its stars, doors, gods, and cach cuc - is interpretation and SHALL remain in the cited AI layer (FR-RAG-003), never in this FR (strategy 7, Claude-03 s7.3: chon dung than roi doc cung cua no ... do tang AI ho tro, luon trich nguon). The output SHALL carry only located facts (role, symbol, palace), no meaning strings. The QiMen engine is heavily school-variant, so when the AI later reads a dung than's palace it must name the school it reads under; that stamping is already carried by the chart's `co_truong_phai` (FR-PLAT-002).

## §2 - Why this design (rationale for humans)

Dung than selection is the bridge from a question to a chart. Unlike LiuRen, which takes its dung than through luc than kinship, QiMen assigns a dung than to each kind of task by convention (Claude-03 s7.3), then reads the palace that dung than sits in. Encoding that convention as a table - question type to (role, symbol) - and then locating each symbol on the assembled chart is a small, deterministic step that gives the interpretation layer exactly what it needs: for a wealth question, here is the palace of the day stem (self), the palace of the hour stem (wealth), the palace of Sinh mon (profit), and so on. The AI then reads those palaces; it does not have to know the selection convention.

Keeping selecting and locating on the engine side, and reading on the AI side, holds the platform's fact / verdict boundary precisely (strategy 7). Which symbol represents wealth for a cau tai question is a documented convention, not a judgment; where that symbol sits on this chart is a lookup against an oracle-gated plate. Both are reproducible and testable like the rest of the engine. What the palace means - is the wealth star well-placed, is it under a hung cach - is interpretation, cited to Yen Ba Dieu Tau Ca and the commentaries, and it stays in the AI layer. Emitting only located facts (no meaning) is what enforces that split at the type level.

Reproducing the s7.3 table verbatim as data, with a source-parity test, is the same discipline as the cach cuc pattern file (FR-QMDG-005): the canonical convention lives in one reviewable place, checked against the source, not scattered through interpretation prompts where it could drift silently.

## §3 - Contract (selection table + location)

### The s7.3 dung than table (Claude-03 s7.3, reproduced verbatim)

| Loai viec | Dung than chinh |
|---|---|
| Cau tai | Nhat can la minh, thoi can la tai, sinh mon la loi, truc phu la chu hang, luc hop la nguoi moi gioi, khai mon la cua hang |
| Su nghiep cong danh | Khai mon la chuc quan, truc phu la cap tren |
| Hon nhan | At la nu, Canh la nam, luc hop la mai moi va hon su |
| Kien tung | Khai mon va truc phu la phia quan, Canh la doi phuong, nhat can la minh |
| Xuat hanh | Xem khai huu sinh mon va phuong cua chung, cung dich ma |
| Benh tat | Thien Nhue la sao benh, Thien Tam la sao thuoc va thay |
| Canh tranh chu khach | Nhat can la chu, thoi can la khach, so hai ben |
| Hop tac | Luc hop la quan he hop tac, xet sinh khac hai ben |

### Types (`crates/cyberos-qimen/src/dung_than.rs`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum LoaiCauHoi {
    CauTai,             // cau tai
    SuNghiepCongDanh,   // su nghiep cong danh
    HonNhan,            // hon nhan
    KienTung,           // kien tung
    XuatHanh,           // xuat hanh
    BenhTat,            // benh tat
    CanhTranhChuKhach,  // canh tranh chu khach
    HopTac,             // hop tac
}

/// The role a dung than plays in the question (self, wealth, opponent, ...).
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Vai {
    Minh, Tai, Loi, ChuHang, NguoiMoiGioi, CuaHang,     // cau tai
    ChucQuan, CapTren,                                   // su nghiep
    Nu, Nam, MaiMoi,                                     // hon nhan
    PhiaQuan, DoiPhuong,                                 // kien tung
    Huong, DichMa,                                       // xuat hanh
    SaoBenh, SaoThuoc,                                   // benh tat
    Chu, Khach,                                          // canh tranh chu khach
    QuanHeHopTac,                                        // hop tac
}

/// The chart symbol that stands for a role. Located on the assembled chart.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case", tag = "kind", content = "val")]
pub enum KyHieu {
    NhatCan,            // the day stem of THIS chart (from lich_phap.tu_tru.ngay)
    ThoiCan,            // the hour stem of THIS chart (from lich_phap.tu_tru.gio)
    Can(Can),           // a fixed stem, e.g. 乙 (At), 庚 (Canh)
    Mon(BatMon),        // a fixed door, e.g. 開門 (Khai), 生門 (Sinh), 休門 (Huu)
    Sao(CuuTinh),       // a fixed star, e.g. 天芮 (Thien Nhue), 天心 (Thien Tam)
    Than(BatThan),      // a fixed god, e.g. 值符 (Truc phu), 六合 (Luc hop)
    DichMa,             // the post-horse, derived from the chart's chi
}

/// A selected dung than located on the assembled chart. Facts only - no meaning.
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DungThan {
    pub vai: Vai,
    pub ky_hieu: KyHieu,
    pub cung: Vec<u8>,        // palace(s) 1..=9 the symbol occupies on THIS chart; may be several (e.g. the cat doors)
}
```

### Entry point

```rust
/// Select the dung than for a question type (from the s7.3 table) and locate each on the
/// assembled QiMen chart. Deterministic: selection is a convention, location is a lookup.
/// Errors if `la_so.he != KyMon`.
pub fn dung_than(loai: LoaiCauHoi, la_so: &LaSo) -> Result<Vec<DungThan>, DungThanError>;

/// The static selection map (question type -> (role, symbol) list), reproduced from s7.3.
pub fn selection(loai: LoaiCauHoi) -> &'static [(Vai, KyHieu)];
```

`selection` returns the s7.3 mapping as data; `dung_than` runs `selection`, then locates each `KyHieu` on the chart: `NhatCan` / `ThoiCan` read the day / hour stem from `lich_phap.tu_tru` and find the palace holding that stem on the thien / dia ban; `Can` / `Mon` / `Sao` / `Than` find the palace of that fixed symbol on the relevant plate; `DichMa` derives the ma from the chart's chi and returns its palace. `Huong` (xuat hanh) is expressed as the palaces of the three cat doors (whose palace is their direction). The result carries only role, symbol, and palace - the interpretation branch reads the palace.

## §4 - Acceptance criteria

1. `selection` reproduces the Claude-03 s7.3 table exactly for all eight question types: cau tai (nhat can = minh, thoi can = tai, sinh mon = loi, truc phu = chu hang, luc hop = nguoi moi gioi, khai mon = cua hang), su nghiep cong danh (khai mon = chuc quan, truc phu = cap tren), hon nhan (At = nu, Canh = nam, luc hop = mai moi), kien tung (khai mon + truc phu = phia quan, Canh = doi phuong, nhat can = minh), xuat hanh (khai / huu / sinh mon + phuong + dich ma), benh tat (Thien Nhue = sao benh, Thien Tam = sao thuoc), canh tranh chu khach (nhat can = chu, thoi can = khach), hop tac (luc hop = quan he hop tac). A source-parity test asserts it.
2. `dung_than` locates each selected symbol on an assembled FR-QMDG-006 chart: the day / hour stems resolve to their palaces, the fixed doors / stars / gods resolve to theirs, and dich ma resolves to the ma palace; a fixture asserts the located palaces for representative charts.
3. Multi-palace roles are handled: xuat hanh returns the palaces of the three cat doors (Khai, Huu, Sinh) as the `Huong` symbols; a role may carry several `cung`.
4. The output carries facts only - `vai`, `ky_hieu`, `cung` - and no meaning / verdict field; a test asserts there is no interpretation string in `DungThan`.
5. `dung_than` errors with a typed `DungThanError` when `la_so.he != KyMon`, never mis-locating against a non-QiMen chart.
6. Determinism: the same `(loai, la_so)` yields the identical located dung than every time.

## §5 - Verification

- `tests/dung_than.rs`: the source-parity test (the `selection` map versus the s7.3 table, all eight types); the location test over `fixtures/dung_than_cases.json` (assembled charts plus expected located palaces per question type); the multi-palace (xuat hanh) case; the wrong-`he` error case; the facts-only assertion.
- Location correctness leans on FR-QMDG-006: the fixture charts are oracle-gated la so, so a mis-location is caught against a known-correct plate. No separate kinqimen gate is needed here (selection is a convention, location is a lookup on an already-gated chart).
- Determinism: `dung_than` run 1,000 times on one fixture returns an equal vector each time.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-qimen -- -D warnings`, `cargo test -p cyberos-qimen`.

## §6 - Implementation skeleton

1. `dung_than.rs`: `LoaiCauHoi`, `Vai`, `KyHieu`, `DungThan`, `DungThanError`.
2. The static `SELECTION` table transcribed from s7.3; `selection(loai)` returns its slice.
3. `dung_than(loai, la_so)`: guard `he == KyMon`; for each `(vai, ky_hieu)`, locate the symbol (day / hour stem from `lich_phap.tu_tru`, fixed symbols on the plates, dich ma from the chi) and collect the palace(s).
4. Build `fixtures/dung_than_cases.json` from FR-QMDG-006 charts with expected located palaces; wire the source-parity, location, multi-palace, wrong-`he`, and determinism tests.

## §7 - Dependencies

Depends on FR-QMDG-006 (the assembled QiMen chart this FR reads; `dung_than` locates symbols on the la so `ban` and needs the `lich_phap` context from FR-CORE-005 for the day / hour stems and dich ma). Emits located facts consumed by the interpretation branch: FR-RAG-003 reads the located palace and writes the cited interpretation, and FR-STRAT-003 (chu-khach decision framework) uses the chu / khach dung than of the canh tranh chu khach type. Note for a human: nothing in the catalog lists FR-QMDG-007 in its `depends_on`, so `blocks` is empty; the FR-RAG-003 / FR-STRAT-003 edges are runtime consumers, recorded in `related_frs`.

## §8 - Example payloads

The located dung than for a cau tai question on an assembled chart (abridged):

```json
{
  "loai_cau_hoi": "cau_tai",
  "dung_than": [
    { "vai": "minh",           "ky_hieu": { "kind": "nhat_can" },              "cung": [4] },
    { "vai": "tai",            "ky_hieu": { "kind": "thoi_can" },              "cung": [9] },
    { "vai": "loi",            "ky_hieu": { "kind": "mon", "val": "生門" },     "cung": [1] },
    { "vai": "chu_hang",       "ky_hieu": { "kind": "than", "val": "值符" },    "cung": [8] },
    { "vai": "nguoi_moi_gioi", "ky_hieu": { "kind": "than", "val": "六合" },    "cung": [3] },
    { "vai": "cua_hang",       "ky_hieu": { "kind": "mon", "val": "開門" },     "cung": [6] }
  ]
}
```

The interpretation branch reads each `cung` (its stars / doors / gods / cach cuc) and writes the cited reading; this FR stops at the located facts.

## §9 - Open questions

- Where the located dung than lives: a side artifact the API requests after assembly, or a stamped `ban.dung_than` view. Default: a pure function over the assembled la so (this FR), so the sealed FR-PLAT-002 envelope is not re-versioned; if profiling later shows the interpretation path always needs it, stamping `ban.dung_than` when `dau_vao.loai_cau_hoi` is present becomes a versioned PLAT-002 change, not a local edit.
- s7.3 completeness: the table lists the common question types, not an exhaustive canon. Default: encode exactly the eight s7.3 types now; new types are added as data with a source citation, re-running the parity test.
- Dich ma derivation: the ma rule keys off a chi (day or hour). Default: derive dich ma from the hour branch per the standard tam-hop ma rule, taking the chi from `lich_phap`; document the choice and flag it if a school variant needs the day branch.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Selection drift | the map diverges from s7.3 | source-parity test fails against the s7.3 table |
| Engine reads meaning | `DungThan` carries an interpretation string | facts-only test fails; selecting + locating only (strategy 7) |
| Wrong-`he` mis-location | a LiuRen / TaiYi chart passed in | typed `DungThanError`; never locate against a non-QiMen chart |
| Missing multi-palace | xuat hanh returns one door, not three | multi-palace test fails; the three cat doors are all located |
| Stale stem lookup | day / hour stem read from the wrong `lich_phap` field | location fixture fails; `NhatCan` / `ThoiCan` read `tu_tru.ngay` / `tu_tru.gio` |
| Non-deterministic output | palace order varies run to run | determinism test (1,000x) fails; output is stably ordered |

## §11 - Notes

This is a small P1 follow-on to the QiMen assembly gate, and it sits exactly on the fact / verdict boundary (strategy 7, Claude-03 s7.3). Selecting the dung than for a question type is a documented convention and locating it on the chart is a lookup, so both are the engine's deterministic job; reading what the palace means is the cited AI layer's job. Keep the s7.3 table as data with a source-parity test, like the FR-QMDG-005 cach cuc file, so the convention lives in one reviewable place and cannot drift into an interpretation prompt. The output is facts only - role, symbol, palace - which is what lets FR-RAG-003 read the palace and cite the meaning without the engine ever asserting it. refs Claude-03 s7.3.
