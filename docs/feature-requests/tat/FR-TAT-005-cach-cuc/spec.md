---
id: FR-TAT-005
title: "Cach cuc + chu-khach thang bai - recognize the position cach between Thai At and the tuong (掩 Yem / 迫 Bach / 關 Quan / 囚 Tu / 擊 Kich / 格 Cach / 對 Doi) and compute the four deterministic victory criteria (hoa vs bat hoa on the toan, truong vs doan, tam tai du vs khuyet, the cach set); emits the facts, leaves the verdict to the cited AI layer; extends the ban for he=thai_at and fills the envelope cach_cuc"
module: TAT
priority: SHOULD
status: done
phase: P2
slice: 4
lang: rust
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 3.4, strategy 4.3, strategy 4.4, Claude-04 s6, Claude-04 s8.3, Grok-30]
related_frs: [FR-TAT-001, FR-TAT-002, FR-TAT-003, FR-TAT-006, FR-PLAT-002, FR-RAG-003]
depends_on: [FR-TAT-003]
blocks: [FR-TAT-006]
new_paths:
  - crates/cyberos-thaiat/src/cachcuc.rs
  - crates/cyberos-thaiat/src/thangbai.rs
  - crates/cyberos-thaiat/tests/cachcuc_oracle.rs
  - crates/cyberos-thaiat/tests/fixtures/cachcuc_kintaiyi.csv
---

## §1 - Description (BCP-14 normative)

This FR reads the positional relationships of a cast Thai At chart into named cach and into the four deterministic criteria that a host-versus-guest reading rests on. It extends the `cyberos-thaiat` crate, consuming the tuong and toan of FR-TAT-003 and the Thai At seat of FR-TAT-002. It produces facts only; the victory verdict itself belongs to the cited AI layer (Claude-04 s6.3, tat module notes).

The module SHALL recognize the cach between Thai At and the tuong from their relative positions on the ring (Claude-04 s6.1): 掩 Yem (a khach muc or khach tuong sharing Thai At's palace), 迫 Bach (a tuong in the palace immediately before or after Thai At), 關 Quan (a chu muc or chu tuong sharing Thai At's palace, or two same-side tuong sharing a palace), 囚 Tu (a chu or khach dai tuong sharing Thai At's palace), 擊 Kich (Thuy Kich adjacent to Thai At - the palace before is ngoai kich, the palace after is noi kich), 格 Cach (a tuong or khach muc in the palace opposite Thai At), 對 Doi (Thai At and a tuong in two opposed palaces). It SHALL support the compound cach noted in Thong Tong Bao Giam quyen sau (De hiep, Tu quach co, Tu quach do) when several tuong fall into yem / bach / kich together.

The module SHALL compute the four victory criteria as deterministic facts (Claude-04 s6.2): hoa vs bat hoa (compare chu toan with khach toan; the larger side generally holds the advantage); truong vs doan (the FR-TAT-003 label per side - truong at eleven or above tends to win, doan at nine or below tends to lose); tam tai (三才, whether the three layers Thien / Dia / Nhan are all present - du, or one is missing - khuyet); and the cach set above. The module SHALL surface the five special conditions 掩 迫 關 囚 擊 as states read from relative position (Claude-04 s8.3), not as separately placed components.

The module SHALL treat these outputs as the deterministic facts and SHALL NOT emit a final "who wins" verdict: reading hoa / bat hoa, truong / doan, tam tai, and the cach into a judgment about fortune or victory is the interpretation branch's job, retrieval-grounded, cited to Kim Kinh Thuc Kinh / Thong Tong Bao Giam, and AIDisclosure-labeled (Claude-04 s6.3, strategy 4.4). The module SHALL extend the `ban` for `he = "thai_at"` with `tam_tai` and SHALL map each recognized cach into an envelope-level `cach_cuc` entry (FR-PLAT-002 `CachCuc`: id, Han name, cung, polarity, citations). The oracle for the recognized cach is kintaiyi.

## §2 - Why this design (rationale for humans)

The cach are not new components; they are predicates over positions already fixed by FR-TAT-002 and FR-TAT-003 (Claude-04 s8.3). So the right shape is a recognition pass: after everything is placed, walk the tuong against Thai At's palace and label the same-palace / adjacent / opposite relationships. Keeping this as a read-only pass over placed positions means it cannot perturb the chart, and it keeps the failure surface small - a cach is either correctly recognized or not, checkable against kintaiyi.

The hard line this FR draws is between fact and verdict. Thai At speaks to the largest matters - the fate of a state, long waves of rise and fall - so the interpretation layer must be especially cautious and explicit about limits (tat module notes, Claude-04 s6.3). The engine's contract is therefore to emit the four criteria as data (which side's toan is larger, each side's truong / doan, tam tai du or khuyet, the cach set) and stop; the AI layer, with citations and an AIDisclosure badge and a HumanReviewGate, turns those facts into a reading. Encoding that boundary in this FR is the technical expression of the product's positioning as heritage education, not fortune-telling (strategy 4.4, section 7).

Tam tai and truong / doan are singled out as the two most quantitative criteria (Claude-04 s6.3): both are exact functions of the placed chart, so the engine computes them and presents them plainly, while hoa / bat hoa and the cach carry more interpretive weight and are handed up with their positions but without a verdict. Splitting this out as a SHOULD, after the MUST spine (FR-TAT-001..003, 006), means the engine can ship a valid envelope with an empty `cach_cuc` and gain the cach recognition and tam tai as an enrichment.

## §3 - Contract (algorithm and types)

### The cach between Thai At and the tuong (Claude-04 s6.1, reproduced faithfully)

| Cach | Dinh nghia | Ben |
|---|---|---|
| 掩 Yem | Khach muc hoac khach tuong cung cung Thai At | Khach |
| 迫 Bach | Tuong o cung ngay truoc hoac sau Thai At | Chu va khach |
| 關 Quan | Chu muc hoac chu tuong cung cung Thai At; hoac hai tuong cung ben chung cung | Chu |
| 囚 Tu | Chu hoac khach dai tuong cung cung Thai At | Dai tuong |
| 擊 Kich | Thuy Kich ke Thai At; cung truoc la ngoai kich, cung sau la noi kich | Khach |
| 格 Cach | Tuong hoac khach muc o cung doi xung Thai At | Doi xung |
| 對 Doi | Thai At va tuong o hai cung xung nhau | Doi xung |

Thong Tong Bao Giam quyen sau: cung cung goi Quan goi Tu, cung cung voi khach goi Yem, cung truoc sau mot cung goi Bach, cung xung goi Cach. Compound cach (several tuong in yem / bach / kich together): De hiep, Tu quach co, Tu quach do.

### The five special conditions as read-from-position states (Claude-04 s8.3)

| Dieu kien | Y nghia |
|---|---|
| 掩 Yem | Che, a component is covered, its posture is limited |
| 迫 Buc | Ep, pressed close, a crowded posture |
| 關 Quan | Ai, blocked at a pass, hard to get through |
| 囚 Tu | Giam, penned in, a stuck posture |
| 擊 Kich | Danh, struck or striking, a contending posture |

These are not extra placements; after every component is seated (FR-TAT-002 / FR-TAT-003), one pass reads them from the relative positions of Thai At and the tuong and records them.

### The four victory criteria (Claude-04 s6.2 / s6.3, facts only)

```
def luan_bon_tieu_chi(cac_toan, cach_cuc, ban):
    hoa        = compare(cac_toan.chu_toan, cac_toan.khach_toan)     # larger side has the edge (relative fact)
    truong_doan = (cac_toan.chu_truong_doan, cac_toan.khach_truong_doan)  # from FR-TAT-003 (>=11 / <=9)
    tam_tai    = "du" if all_three_present(ban, "thien", "dia", "nhan") else "khuyet"
    return {                       # DETERMINISTIC FACTS ONLY - no "who wins" verdict here
        "hoa": hoa, "truong_doan": truong_doan,
        "tam_tai": tam_tai, "cach_cuc": cach_cuc
    }
    # the verdict (fortune / victory reading) is the AI layer's job: retrieval-grounded, cited, AIDisclosure
```

### Public types (`crates/cyberos-thaiat/src/`)

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum Cach { Yem, Bach, Quan, Tu, Kich, Cach, Doi }

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BienTheKich { NoiKich, NgoaiKich }        // palace after / before Thai At

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum TamTai { Du, Khuyet }                      // three layers present / one missing

#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub struct CachCucTat {
    pub cach: Cach, pub han: &'static str,
    pub tuong: &'static str,       // which tuong triggered it (van_xuong, thuy_kich, ...)
    pub cung: u8,                  // the palace involved
    pub bien_the: Option<BienTheKich>,   // set for 擊 Kich only
}

pub fn nhan_dien_cach_cuc(bat_tuong: &BatTuong, thai_at_ring: u8) -> Vec<CachCucTat>;
pub fn tinh_tam_tai(ban: &ThaiAtBan) -> TamTai;
pub fn map_to_envelope_cach_cuc(cach: &[CachCucTat]) -> Vec<CachCuc>;   // FR-PLAT-002 CachCuc
```

## §4 - Acceptance criteria

1. `nhan_dien_cach_cuc` recognizes each of the seven cach from position: same-palace (Yem / Quan / Tu depending on which tuong), immediately-before-or-after (Bach), adjacent Thuy Kich (Kich, with noi / ngoai per after / before), and opposed palace (Cach / Doi); a crafted chart per cach is asserted against kintaiyi.
2. The `擊 Kich` variant is `noi_kich` when Thuy Kich sits in the palace after Thai At and `ngoai_kich` when before; a unit test pins both.
3. `tinh_tam_tai` returns `du` when Thien / Dia / Nhan are all present and `khuyet` when one is missing; a unit test enumerates a du and a khuyet chart.
4. The four criteria are emitted as facts (the hoa comparison, both truong / doan labels, tam tai, the cach set) and the module exposes no "who wins" verdict field; a test asserts the absence of a verdict in the output type.
5. Each recognized cach maps to an envelope `cach_cuc` entry with a stable id, its Han name, the palace, a polarity, and a citation to Kim Kinh Thuc Kinh / Thong Tong Bao Giam; the envelope `cach_cuc` array validates against FR-PLAT-002.
6. `ban.tam_tai` and the envelope `cach_cuc` round-trip through the la so envelope under `he = "thai_at"`.

## §5 - Verification

- Unit: one crafted chart per cach (seven), the Kich noi / ngoai split, a du and a khuyet tam tai, the no-verdict assertion.
- Property: `nhan_dien_cach_cuc` is a pure function of the placed positions (running it twice on the same chart yields the same set; it never mutates the chart); every emitted `cach_cuc` carries at least one citation.
- Oracle: `tests/cachcuc_oracle.rs` loads `fixtures/cachcuc_kintaiyi.csv` (generated once from kintaiyi, per epoch, over many charts covering all seven cach and the compounds) and asserts the recognized cach set matches exactly. Feeds the FR-TAT-006 gate for the cach portion.
- Boundary: a chart with several tuong in yem / bach / kich together (the compound De hiep / Tu quach co / Tu quach do) and a chart with no cach at all (empty set, valid).
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-thaiat -- -D warnings`, `cargo test -p cyberos-thaiat`.

## §6 - Implementation skeleton

1. `cachcuc.rs`: the `Cach` enum, the position predicates (same palace, before / after, opposed), the Kich noi / ngoai split, the compound-cach detection, and `nhan_dien_cach_cuc` as a read-only pass over FR-TAT-002 / FR-TAT-003 positions.
2. `thangbai.rs`: `tinh_tam_tai`, the four-criteria aggregation `luan_bon_tieu_chi` (facts only), and `map_to_envelope_cach_cuc` producing FR-PLAT-002 `CachCuc` with ids, Han names, polarity, and citations.
3. Assign each cach a stable id (e.g. `taiyi_yem`, `taiyi_kich_noi`) and a citation string; keep the polarity contextual and conservative (favorable / unfavorable to a side per s6.2, else trung), leaving the verdict to the AI layer.
4. Extend the `he = "thai_at"` `ban` with `tam_tai`; feed the `cach_cuc` list to the envelope (the envelope array is filled by FR-TAT-006 assembly).
5. Generate the kintaiyi cach fixture once (documented script, not run in CI) and commit; wire the oracle, property, and boundary tests.

## §7 - Dependencies

Depends on FR-TAT-003 (the tuong positions and the toan with their truong / doan labels) and transitively on FR-TAT-002 (the Thai At seat and the ring) and FR-TAT-001. Soft-feeds FR-TAT-006: the assembly's MUST path emits a valid envelope with an empty `cach_cuc` and no `tam_tai`; this FR enriches it with the recognized cach and tam tai, so it blocks the cach / tam-tai portion of the FR-TAT-006 gate, not the yearly assembly itself. Feeds FR-RAG-003 (the interpretation branch reads these facts and never writes them) - the cited victory reading is built there, not here.

## §8 - Example payloads

Envelope fragment after cach recognition (values illustrative; the cach set is pinned to kintaiyi):

```json
{ "ban": {
    "tich": { "...": "from FR-TAT-001" }, "thai_at_cung": 1, "thai_at_ring": 14,
    "thap_luc_than": { "...": "FR-TAT-002" }, "bat_tuong": { "...": "FR-TAT-003" },
    "cac_toan": { "chu_toan": 15, "khach_toan": 8, "chu_truong_doan": "truong", "khach_truong_doan": "doan" },
    "tam_tai": "du"
  },
  "cach_cuc": [
    { "id": "taiyi_yem", "name": "掩", "cung": 1, "polarity": "hung",
      "citations": ["Thong Tong Bao Giam q6"] },
    { "id": "taiyi_cach", "name": "格", "cung": 5, "polarity": "trung",
      "citations": ["Kim Kinh Thuc Kinh"] }
  ],
  "co_truong_phai": { "epoch": "kim_kinh", "dem_toan": "truoc_thai_at" } }
```

(The `cach_cuc` array is the envelope-level list of FR-PLAT-002 `CachCuc`; `tam_tai` lives inside `ban`. No "who wins" field appears - that reading is the AI layer's, cited and AIDisclosure-labeled.)

## §9 - Open questions

- Polarity of a cach in the envelope `CachCuc` is contextual in Thai At (favorable to one side is unfavorable to the other, s6.2), unlike the cleaner cat / hung of QiMen. Default: assign polarity conservatively per the s6.2 "bat loi" guidance where the source is explicit, else `trung`, and let the AI layer weigh it. Revisit if the chart UI (CHART-003) needs a firmer polarity.
- Tam tai's Thien / Dia / Nhan layers (s6.3) are described as "three layers of information about heaven, earth, and man in the chart"; the exact components that constitute each layer are pinned to kintaiyi (or a second source) before the du / khuyet test is locked.
- The compound cach (De hiep, Tu quach co, Tu quach do) are named but thinly defined in s6.1; their precise trigger (how many tuong, in which relation) is confirmed against kintaiyi, and left recognized-but-unlabeled if the oracle does not distinguish them.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Engine emits a victory verdict | "who wins" computed in Rust | forbidden by the output type (no verdict field); a test asserts its absence; the reading is the AI layer's |
| Cach mis-recognized | wrong position predicate (before vs after, opposed vs adjacent) | crafted per-cach tests and the kintaiyi fixture diverge |
| Kich noi / ngoai swapped | after / before Thai At inverted | dedicated test pins noi = after, ngoai = before |
| Cach without citation | envelope `CachCuc` emitted with empty citations | property test requires >= 1 citation per cach |
| Tam tai wrong | a layer counted present when missing | du / khuyet enumerated test vs the oracle |
| Recognition mutates the chart | pass writes back into placed positions | property test asserts the chart is unchanged after recognition |

## §11 - Notes

This FR is a read-only recognition pass plus a fact aggregation; its discipline is the fact / verdict boundary. Thai At luan cai lon - national fortune, long waves - so the engine must stop at facts (the cach set, tam tai du / khuyet, truong / doan, the hoa comparison) and hand the reading to a cautious, cited, human-gated AI layer (Claude-04 s6.3, tat module notes, strategy 4.4 and section 7). Recognizing the cach as predicates over already-placed positions keeps the pass safe and small; the seven cach and the compounds are pinned to kintaiyi. As a SHOULD after the MUST spine, it upgrades a bare envelope (empty `cach_cuc`, no `tam_tai`) into a full one, and its outputs are exactly what FR-RAG-003 consumes to build the interpretation - which it must never write back.
