---
id: FR-CORE-007
title: "Ganzhi primitives + relations - 10 thien can / 12 dia chi / 60 giap ty, ngu hanh of each, sinh + khac cycles, chi hinh/xung/pha/hai/hop (luc hop, tam hop, luc xung), index round-trip, pure lookup"
module: CORE
priority: MUST
status: implementing
phase: P0
slice: 1
lang: rust
effort_h: 8
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [strategy 4.4, Claude-06 s3.2, Claude-01]
related_frs: [FR-CORE-003, FR-CORE-004, FR-QMDG-005, FR-LN-002, FR-TAT-003]
depends_on: [FR-PLAT-001]
blocks: [FR-QMDG-005, FR-LN-002, FR-TAT-003]
new_paths:
  - crates/cyberos-lichphap/src/ganzhi.rs
  - crates/cyberos-lichphap/src/relations.rs
  - crates/cyberos-lichphap/tests/ganzhi_relations.rs
---

## §1 - Description (BCP-14 normative)

This FR provides the can chi (干支) primitives and their relations - the atomic vocabulary that every engine speaks. It is pure lookup and modular arithmetic over the ten thien can, the twelve dia chi, and the sixty-term giap ty cycle, plus the ngu hanh (five phases) of each and the classical branch relations (hinh, xung, pha, hai, hop). It is deliberately dependency-light so it can be built in parallel with the astronomy layer and heavily unit-tested (Claude-01, Claude-06 s3.2).

The module SHALL define the ten thien can, the twelve dia chi, and the sixty giap ty pairs, with total conversion between a can/chi/giap-ty value and its integer index and back. It SHALL define the ngu hanh of each can and each chi, the sinh (generating) cycle and the khac (controlling) cycle over the five phases. It SHALL define the dia chi relations: luc hop and tam hop (harmonies), luc xung (clashes), luc hai (harms), luc pha (breaks), and the three groups of hinh (punishments) including the tu hinh (self-punishment). Every relation SHALL be exposed both as data (the tables) and as a queryable predicate (does chi A clash chi B). All lookups MUST round-trip: `index -> value -> index` is identity across the whole domain.

## §2 - Why this design (rationale for humans)

The three engines diverge in how they build and read a chart, but they all reduce to statements about can and chi and the phase relations between them (Claude-01). QiMen cach cuc detection asks whether the ten stems overcome one another (thap can khac ung); LiuRen tu khoa and luc than ask whether the day stem generates or controls a branch and whether branches harmonize or clash; TaiYi and the derived states ask for the phase of a stem or the seasonal strength of a phase. If each engine re-encoded "Moc controls Tho" or "Ty clashes Ngo," the tables would drift and a fix in one would miss the others. One primitive layer, exhaustively tested, is the cheapest way to keep them consistent.

Keeping every relation as both data and predicate serves two readers: the rule engine (RULE-002) and the knowledge-graph edge taxonomy (Claude-06 s3.2) consume the tables as data, while the engines call the predicates in casting code. Because the domain is small and closed (10 x 12 x 60 and a handful of relation sets), the whole surface can be enumerated in tests, which is exactly the kind of hard, cheap correctness the platform wants at its base. The classical Han is kept in every table because these relations are read and checked by domain experts against texts, and the glyph is the unambiguous identity.

## §3 - Contract (types, tables, relations)

### Primitives

```rust
pub enum Can { Giap, At, Binh, Dinh, Mau, Ky, Canh, Tan, Nham, Quy }   // 甲乙丙丁戊己庚辛壬癸, index 0..10
pub enum Chi { Ty, Suu, Dan, Mao, Thin, Ty2, Ngo, Mui, Than, Dau, Tuat, Hoi } // 子丑寅卯辰巳午未申酉戌亥, 0..12
pub enum NguHanh { Moc, Hoa, Tho, Kim, Thuy }                          // 木火土金水
pub struct GiapTy(pub u8);                                            // 0..60, 0 = 甲子
// Chi::Ty2 is 巳 (snake); Chi::Ty is 子 (rat). Distinct glyphs, kept apart in code.
pub fn giap_ty_from_can_chi(c: Can, z: Chi) -> GiapTy;                 // valid only for the 60 legal pairs
pub fn can_chi_of(g: GiapTy) -> (Can, Chi);
```

### Ngu hanh of can and chi

| Can | Ngu hanh | Chi | Ngu hanh |
|---|---|---|---|
| 甲 乙 | 木 Mộc | 寅 卯 | 木 Mộc |
| 丙 丁 | 火 Hỏa | 巳 午 | 火 Hỏa |
| 戊 己 | 土 Thổ | 辰 戌 丑 未 | 土 Thổ |
| 庚 辛 | 金 Kim | 申 酉 | 金 Kim |
| 壬 癸 | 水 Thủy | 子 亥 | 水 Thủy |

### Sinh and khac (Claude-01)

```
sinh (sinh ra, generating):   木 -> 火 -> 土 -> 金 -> 水 -> 木
khac (khac che, controlling): 木 -> 土 -> 水 -> 火 -> 金 -> 木
```

Predicates: `sinh(a, b)` iff b is the phase a generates; `khac(a, b)` iff b is the phase a controls. Their inverses (`duoc_sinh`, `bi_khac`) follow.

### Dia chi relations

Luc hop (六合, six harmonies):

```
子丑  寅亥  卯戌  辰酉  巳申  午未
```

Tam hop (三合, three harmonies) and the phase each trine forms:

```
申子辰 -> 水 Thủy    亥卯未 -> 木 Mộc    寅午戌 -> 火 Hỏa    巳酉丑 -> 金 Kim
```

Luc xung (六冲, six clashes):

```
子午  丑未  寅申  卯酉  辰戌  巳亥
```

Luc hai (六害, six harms):

```
子未  丑午  寅巳  卯辰  申亥  酉戌
```

Luc pha (六破, six breaks):

```
子酉  午卯  申巳  寅亥  辰丑  戌未
```

Hinh (刑, punishments):

```
Vo an chi hinh:   寅巳申   (the tri-punishment)
Tri the chi hinh: 丑戌未
Vo le chi hinh:   子卯
Tu hinh (self):   辰辰  午午  酉酉  亥亥
```

### Relation API

```rust
pub enum ChiQuanHe { LucHop, TamHop, LucXung, LucHai, LucPha, Hinh, TuHinh }
pub fn quan_he(a: Chi, b: Chi) -> Vec<ChiQuanHe>;   // all relations that hold for the (unordered) pair
pub fn tam_hop_cua(z: Chi) -> (Chi, Chi, NguHanh);  // the other two of z's trine + its phase
```

## §4 - Acceptance criteria

1. Round-trip identity: for all 10 can, 12 chi, and 60 giap ty, `index -> value -> index` is identity; `giap_ty_from_can_chi` accepts exactly the 60 legal pairs and `can_chi_of` inverts it.
2. Ngu hanh assignment is correct for all 10 can and all 12 chi against the tables above (辰 戌 丑 未 all Thổ; 子 亥 both Thủy).
3. Sinh and khac cycles are correct for all 5 phases each way; `khac(Moc, Tho)` and `sinh(Moc, Hoa)` hold, and non-relations are false.
4. Every branch relation set is exhaustively correct: 6 luc hop, 4 tam hop trines (with phase), 6 luc xung, 6 luc hai, 6 luc pha, the three hinh groups and 4 tu hinh; `quan_he` returns all and only the relations that hold for a pair.
5. `子` (Ty, rat) and `巳` (Ty2, snake) are never conflated; a test asserts the two enum variants map to distinct glyphs and distinct relations.

## §5 - Verification

- `tests/ganzhi_relations.rs` enumerates the full domains: 60 giap-ty round-trips, 10+12 ngu-hanh rows, 5+5 sinh/khac rows, and every relation pair, all against the §3 tables.
- Symmetry test: all listed relations are symmetric (`quan_he(a,b) == quan_he(b,a)`), and the trine `tam_hop_cua` is consistent (each member returns the same trine and phase).
- Negative tests: pairs with no relation return an empty `quan_he`; illegal can-chi pairs (e.g. 甲丑) are rejected by `giap_ty_from_can_chi`.
- Gates: `cargo fmt --check`, `cargo clippy -p cyberos-lichphap -- -D warnings`, `cargo test -p cyberos-lichphap`.

## §6 - Implementation skeleton

1. `ganzhi.rs`: the `Can` / `Chi` / `NguHanh` / `GiapTy` types, their glyph and index mappings, the 60-pair legality check, and `giap_ty_from_can_chi` / `can_chi_of`.
2. `relations.rs`: the ngu-hanh-of tables, the sinh/khac cycles as `const` maps, the branch-relation sets as `const` data, and the `quan_he` / `tam_hop_cua` predicates over them.
3. Serialize `Can` / `Chi` / `GiapTy` to their Han glyph (so the calendar output and envelope carry 甲子, not indices), with `Deserialize` accepting the glyph.
4. Add the exhaustive enumerated tests and the symmetry / negative tests.

## §7 - Dependencies

Depends on FR-PLAT-001 (workspace) only - deliberately independent of the astronomy layer so it can proceed in parallel and be joined at integration. Consumed by FR-CORE-003 (pillars use `Can`/`Chi`) and FR-CORE-004 (derived states use phase + sinh/khac). Blocks the relation-consuming engine slices: FR-QMDG-005 (thap can khac ung / cat-hung uses stem overcoming), FR-LN-002 (tu khoa thuong/ha khac and later luc than use sinh/khac and branch relations), FR-TAT-003 (cac toan). NOTE: the master catalog does not list CORE-007 in those FRs' `depends_on` because relations are a shared primitive many slices touch; the dependency is real but soft (build CORE-007 early, wire as engines land) - flag for catalog reconciliation if hard edges are wanted.

## §8 - Example payloads

```rust
quan_he(Chi::Ty, Chi::Ngo)     // => [LucXung]          (子午 clash)
quan_he(Chi::Dan, Chi::Hoi)    // => [LucHop, LucPha]   (寅亥 harmonize and break)
tam_hop_cua(Chi::Than)         // => (Chi::Ty, Chi::Thin, NguHanh::Thuy)   (申子辰 -> 水)
khac(NguHanh::Moc, NguHanh::Tho) // => true             (木 khac 土)
```

## §9 - Open questions

- Do we model the ban-hop (half-harmony) and the hoa (transformation of a hop into its phase), or only the full relations? Decision for MVP: model the full luc hop / tam hop / xung / hai / pha / hinh sets; ban-hop and hoa-cuc are engine-level refinements deferred to whichever engine first needs them (likely LiuRen luc than), added as predicates over this base.
- Should the sixty na-am (nap am, the sound-phase of each giap ty pair) live here? Decision: not in this FR; nap am is a separate 60-entry table added when an engine (TaiYi / QiMen) needs it, layered on `GiapTy` without changing this API.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| 子 / 巳 conflated | Ty (rat) and Ty2 (snake) share a variant | distinct-glyph test fails; keep two enum variants |
| Illegal pair accepted | 甲丑 (odd/even parity broken) passed | `giap_ty_from_can_chi` rejects; only 60 legal pairs |
| khac cycle reversed | 木->金 instead of 木->土 | sinh/khac enumeration fails |
| Relation set incomplete | a xung or hai pair dropped | exhaustive relation test fails |
| Relation asymmetric | `quan_he(a,b) != quan_he(b,a)` | symmetry test fails |
| Index drift | glyph order changed without index update | round-trip identity test fails |

## §11 - Notes

This is the smallest FR in the calendar core and the most re-used - treat its test suite as a specification of the domain, enumerated rather than sampled. Keep the classical Han in every table; the 子/巳 (Ty/Ty2) and 辰戌丑未-all-Thổ cases are exactly where ASCII normalization would introduce a silent error. Same crate `cyberos-lichphap` - this FR adds `ganzhi.rs` and `relations.rs`, the vocabulary the pillars, derived states, and all three engines are written in.
