---
id: FR-RAG-005
title: "Term-sense expansion - expand a query across the layered senses of a classical term (ban nghia base / dan than extended / gia ta phonetic-loan / dien tich allusion) via a curated glossary, weighted and bounded, so retrieval does not miss relevant classical text; sits upstream of FR-RAG-002"
module: RAG
priority: SHOULD
status: done
phase: P2
slice: 1
lang: python
effort_h: 10
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.2, strategy 4.2]
related_frs: [FR-RAG-002, FR-RAG-001, FR-KB-003, FR-RAG-003, FR-RAG-006]
depends_on: [FR-RAG-002]
blocks: []
new_paths:
  - packages/tamthuc_rag/tamthuc_rag/expand.py
  - packages/tamthuc_rag/tamthuc_rag/glossary.py
  - data/glossary/qimen_terms.json
  - data/glossary/liuren_terms.json
  - data/glossary/taiyi_terms.json
  - data/glossary/SENSES.md
  - packages/tamthuc_rag/tests/test_expand.py
  - packages/tamthuc_rag/tests/fixtures/term_sense_sample.json
  - docs/contracts/term-glossary.schema.json
---

## §1 - Description (BCP-14 normative)

This FR widens a query across the layered senses of the classical terms it contains, so retrieval does not miss văn bản cổ that uses a term in an extended, loaned, or allusive sense. It sits upstream of FR-RAG-002: it takes the query text (and system), expands the classical terms it recognizes, and hands FR-RAG-002 an enriched query to retrieve on. It is a recall aid over retrieval; it produces no interpretation and asserts nothing.

A classical term SHALL be expandable across four sense layers (Claude-06 s4.2): bản nghĩa (本義, the base/original sense), nghĩa dẫn thân (引申, the extended sense), nghĩa giả tá (假借, the phonetic-loan sense - a borrowed sound with an unrelated meaning), and nghĩa điển tích (典故, the allusion sense - a reference into a classical story or text). Expansion SHALL be driven by a curated glossary that maps each term to its senses per layer, each sense carrying its own surface forms (Han + romanized + Vietnamese) and a weight. The expander SHALL detect glossary terms in the query, filtered to `system in {system, all}`, and SHALL add the weighted surface forms of their enabled senses, returning an `ExpandedQuery` for FR-RAG-002.

Expansion SHALL be bounded and weighted so it widens recall without drowning the query's intent: the base sense SHALL weigh highest, the extended sense lower, and the phonetic-loan and allusion senses lowest, and the total number of added terms SHALL be capped. Because the giả tá (phonetic-loan) layer carries the highest noise risk - a borrowed sound with an unrelated meaning - it SHALL be off by default and enabled only per-term where the glossary marks it reliable. Expansion SHALL be deterministic given the query and the glossary, SHALL preserve the original query as the highest-weighted signal, and SHALL make no claim and touch no la so field - it operates on query text only.

## §2 - Why this design (rationale for humans)

Văn ngôn văn is compressed and polysemous in a way modern text is not: one term routinely carries a base meaning, an extended meaning grown from it, sometimes a meaning borrowed only for its sound, and sometimes a meaning that only makes sense as a reference to a classical passage (Claude-06 s4.2). A query embedded as-is retrieves passages that match the sense the user happened to phrase, and silently misses passages where the classics use the same term in one of its other senses. That is the exact recall gap this FR closes: by expanding the query through the glossary's sense layers, a question phrased in one sense can still surface a điều that speaks in another. It is the query-side complement to storing three parallel text layers (FR-KB-003) - the store keeps each layer's language, and this FR reaches across the senses within them.

The weighting and the bound are what keep expansion from turning recall into noise. If every sense of every term were added at equal weight, the query would blur and precision would collapse, so the base sense dominates, the extended sense supports, and the loan and allusion senses only nudge. The giả tá layer is singled out because a phonetic loan is, by definition, an unrelated meaning riding on a shared sound; adding it blindly pulls in text about something else entirely, so it stays off unless a curator has vouched for a specific term. Keeping the expander strictly a query-side, claim-free step is deliberate: it changes what gets retrieved, never what gets asserted, so all of the anti-hallucination discipline still lives where it belongs, downstream in FR-RAG-003, and this FR can widen recall without ever being a place where meaning is invented. Its real payoff is measured, not assumed - FR-RAG-006 is where "did expansion help recall without hurting faithfulness" gets a number.

## §3 - Contract (glossary, expander)

### Glossary (`tamthuc_rag/glossary.py`, `data/glossary/<system>_terms.json`)

```python
class SenseLayer(str, Enum):
    ban_nghia = "ban_nghia"      # 本義 base / original
    dan_than = "dan_than"        # 引申 extended
    gia_ta = "gia_ta"            # 假借 phonetic loan (off by default)
    dien_tich = "dien_tich"      # 典故 allusion

class TermSense(BaseModel):
    model_config = ConfigDict(extra="forbid")
    layer: SenseLayer
    gloss: str                   # what this sense means
    surface_forms: list[str]     # words/phrases that carry it (Han + romanized + Viet)
    weight: float                # base > extended > loan/allusion
    reliable: bool = True        # gia_ta senses default reliable=False until curated
    citations: list[str] = []    # optional unit(s) documenting this sense (FR-KB-003)

class TermEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")
    term: str                    # canonical term, e.g. "值符"
    term_han: str | None
    system: System               # qimen | liuren | taiyi | all
    aliases: list[str] = []      # Han / romanized / slug forms that resolve to this term
    senses: list[TermSense]

class TermGlossary:
    def match(self, query: str, system: System) -> list[TermEntry]: ...   # system in {system, all}
    @classmethod
    def load(cls, paths: list[Path]) -> "TermGlossary": ...
```

### Expander (`tamthuc_rag/expand.py`)

```python
DEFAULT_LAYERS = {SenseLayer.ban_nghia, SenseLayer.dan_than, SenseLayer.dien_tich}   # gia_ta off

class ExpandConfig(BaseModel):
    layers: set[SenseLayer] = DEFAULT_LAYERS
    max_added_terms: int = 12        # hard cap
    min_weight: float = 0.1

class ExpandedQuery(BaseModel):
    original: str
    matched_terms: list[str]                 # glossary terms that fired
    added_terms: list[str]                   # surface forms added, capped and de-duped
    weighted_terms: list[tuple[str, float]]  # original terms highest, expansions weighted down
    layers_used: list[SenseLayer]
    def enriched_text(self) -> str: ...       # original + weighted added terms, for FR-RAG-002 to embed
    def query_variants(self) -> list[str]: ... # optional per-sense variants for multi-query retrieval

class TermExpander:
    def __init__(self, glossary: TermGlossary, config: ExpandConfig = ExpandConfig()): ...
    def expand(self, query: str, system: System) -> ExpandedQuery:
        # 1. glossary.match(query, system) -> terms present (system-filtered)
        # 2. for each term, take senses in config.layers; skip gia_ta senses with reliable=False
        # 3. add weighted surface forms; base > extended > allusion; drop below min_weight
        # 4. cap to max_added_terms by weight; keep the original query highest-weighted
        # 5. return ExpandedQuery (deterministic; stable order by weight then form)
```

### The FR-RAG-002 seam

FR-RAG-002's `RetrievalRequest` carries `query: str`. The default integration is single-query: the caller sets `request.query = expanded.enriched_text()` (original plus weighted added terms) and FR-RAG-002 embeds it as one vector - FR-RAG-002 is unchanged. A recall-sensitive mode uses `expanded.query_variants()`: the caller retrieves for each variant and unions the hits into FR-RAG-002's fusion. The default is single-query (cheapest, keeps the interface intact); multi-query is a flag evaluated by FR-RAG-006.

## §4 - Acceptance criteria

1. A query containing a glossary term (e.g. "值符" / "truc phu") expands into `added_terms` drawn from that term's enabled senses, with the base sense weighted above the extended and allusion senses.
2. The per-system filter holds: a `qimen` query matches only `qimen` and `all` terms, never a `liuren`/`taiyi`-only term.
3. The giả tá layer is off by default: a `gia_ta` sense with `reliable = false` contributes nothing unless the layer is enabled and the sense is marked reliable.
4. Expansion is bounded: `added_terms` never exceeds `max_added_terms`, low-weight forms below `min_weight` are dropped, and the original query stays the highest-weighted signal.
5. `enriched_text()` returns the original query plus the weighted expansions in a stable order, and feeding it to a stub FR-RAG-002 retrieves a passage that the bare query missed on the fixture (recall lift shown).
6. Expansion is deterministic and claim-free: identical query + glossary yield an identical `ExpandedQuery`; no la so field is read or written and no interpretation is produced.

## §5 - Verification

- `tests/test_expand.py`: term detection across Han/romanized/alias forms; the per-system filter; the gia_ta-off-by-default and reliable-gate cases; the `max_added_terms` cap and `min_weight` drop; base > extended > allusion weighting; determinism (repeat runs equal); the recall-lift case with a stub FR-RAG-002 retriever over the FR-RAG-001 fixture index (expanded query retrieves a unit the bare query does not).
- Glossary conformance: every `data/glossary/<system>_terms.json` row validates against `docs/contracts/term-glossary.schema.json`; any `gia_ta` sense defaults `reliable=false`; a lint asserts weights are ordered base >= extended >= loan/allusion within a term.
- Claim-free guard: a test asserts `expand` never constructs an `Interpretation` and never accesses a la so envelope - it takes only `query` and `system`.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_rag`, `pytest packages/tamthuc_rag`.

## §6 - Implementation skeleton

1. `glossary.py`: `SenseLayer`, `TermSense`, `TermEntry`, `TermGlossary` (load + match); author `docs/contracts/term-glossary.schema.json`.
2. `expand.py`: `ExpandConfig`, `ExpandedQuery`, `TermExpander.expand` (detect, sense-select, weight, cap, deterministic order).
3. Author `data/glossary/qimen_terms.json` first (the P0/P1 flagship terms - truc phu, the luc nghi tam ky, the headline cách cục terms), then `liuren` and `taiyi` to representative coverage; `data/glossary/SENSES.md` documents the four layers and the weighting convention.
4. Wire the FR-RAG-002 seam: `enriched_text()` for single-query (default) and `query_variants()` for the multi-query flag.
5. Commit `fixtures/term_sense_sample.json` (a few terms across systems, with a deliberate gia_ta case) as the test exemplar.

## §7 - Dependencies

Depends on FR-RAG-002 (this FR widens the query FR-RAG-002 retrieves on; the default single-query integration keeps FR-RAG-002's interface intact). Reads no la so - it operates on the query string and the system only. Related to FR-RAG-001 (the same three-layer chunks its expanded query retrieves over) and FR-KB-003 (the corpus a sense's optional `citations` resolve into, and a natural source for authoring the glossary's senses). Blocks nothing; it is an optional recall enhancement in front of retrieval. Its value is scored by FR-RAG-006, which measures whether expansion lifts recall without hurting faithfulness or precision. The RAG-branch invariant holds trivially here: this FR never produces an interpretation and never touches `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`; the citation and AIDisclosure discipline lives downstream in FR-RAG-003 and is untouched by widening retrieval.

## §8 - Example payloads

```json
// a glossary entry (abbreviated) for a QiMen term, with gia_ta off by default
{ "term": "值符", "term_han": "值符", "system": "qimen", "aliases": ["truc phu", "truc_phu"],
  "senses": [
    { "layer": "ban_nghia", "gloss": "the on-duty talisman star, the chief of the nine stars",
      "surface_forms": ["值符", "truc phu", "chief star"], "weight": 1.0, "citations": ["yba_dieu_003"] },
    { "layer": "dan_than", "gloss": "by extension, the acting/leading party in the chart",
      "surface_forms": ["acting palace", "leading party"], "weight": 0.6 },
    { "layer": "gia_ta", "gloss": "(loan) not used for this term", "surface_forms": [],
      "weight": 0.2, "reliable": false } ] }
```

```json
// ExpandedQuery for "co nen tin nguoi dang truc phu khong"
{ "original": "co nen tin nguoi dang truc phu khong",
  "matched_terms": ["值符"], "layers_used": ["ban_nghia", "dan_than"],
  "added_terms": ["值符", "chief star", "acting palace", "leading party"],
  "weighted_terms": [["co nen tin nguoi dang truc phu khong", 1.0], ["值符", 1.0],
    ["chief star", 1.0], ["acting palace", 0.6], ["leading party", 0.6]] }
```

## §9 - Open questions

- Single enriched query vs multi-query retrieval. Default: single enriched query (keeps FR-RAG-002 unchanged, cheapest); multi-query behind a flag for recall-critical cases. Decide from FR-RAG-006 recall/precision numbers.
- Whether the glossary is hand-authored or bootstrapped from a classical dictionary. Default: hand-author the flagship QiMen terms with a curator, cite senses into FR-KB-003 where a source documents them; bootstrap wider coverage later under FR-KB-004 review.
- How aggressively to enable điển tích (allusion) expansion. Default: on but low-weighted; an allusion pulls in the referenced passage, which helps when the reference is apt and adds noise when it is not - tune the weight from eval, keep it below the base and extended senses.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Over-expansion drowns intent | every sense added at equal weight | base > extended > loan/allusion weighting; `max_added_terms` cap; original stays highest |
| Phonetic-loan noise | a gia_ta sense pulls unrelated text | gia_ta off by default; enabled only per-term with `reliable=true` |
| Cross-system leak | a foreign-system term expands the query | `system in {system, all}` filter on glossary match; isolation test |
| Non-deterministic expansion | unstable ordering of added terms | stable order by (weight desc, form); determinism test |
| Expansion becomes assertion | expander drifts into producing meaning | claim-free guard: `expand` takes only query+system, returns terms, never an interpretation |
| Recall lift unverified | expansion shipped on faith | FR-RAG-006 scores recall vs precision/faithfulness; expansion tuned from the number |

## §11 - Notes

This FR closes a recall gap specific to văn ngôn văn: a query phrased in one sense of a term must still reach classical text that uses another sense. Its discipline is entirely in the weighting and the bound - widen recall, never blur intent - and its safety is that it is claim-free, so it changes what is retrieved and never what is asserted. Author the QiMen glossary first to match the P0/P1 flagship, keep giả tá off unless a curator vouches for a term, and let FR-RAG-006 decide the layer weights from measured recall and faithfulness rather than intuition. The package `tamthuc_rag` is shared with FR-RAG-001/002/003/004/006/007; this FR adds `expand.py` and `glossary.py`, so the RAG branch stays one installable, mypy-clean unit.
