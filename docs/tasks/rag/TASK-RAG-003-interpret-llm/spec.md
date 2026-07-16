---
id: TASK-RAG-003
title: "Prompt library + LLM caller + structured output {beginner/expert/recommendations/citations/confidence} + 3-layer anti-hallucination + AIDisclosure on every output + citation cards; reads the la so, never writes ban/cach_cuc"
module: RAG
priority: MUST
status: done
phase: P0
slice: 1
lang: python
effort_h: 16
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s4.1, Claude-06 s4.3, strategy 4.4, strategy 8]
related_frs: [TASK-RAG-002, TASK-RAG-004, TASK-RAG-006, TASK-RAG-007, TASK-PLAT-002, TASK-WEB-003, TASK-REPORT-001, TASK-STRAT-003, TASK-LEGAL-003]
depends_on: [TASK-RAG-002]
blocks: [TASK-RAG-004, TASK-RAG-006, TASK-RAG-007, TASK-WEB-003, TASK-REPORT-001, TASK-STRAT-003]
new_paths:
  - packages/tamthuc_rag/tamthuc_rag/interpret.py
  - packages/tamthuc_rag/tamthuc_rag/prompt_builder.py
  - packages/tamthuc_rag/tamthuc_rag/prompts/system.md
  - packages/tamthuc_rag/tamthuc_rag/prompts/beginner.md
  - packages/tamthuc_rag/tamthuc_rag/prompts/expert.md
  - packages/tamthuc_rag/tamthuc_rag/llm.py
  - packages/tamthuc_rag/tamthuc_rag/schema.py
  - packages/tamthuc_rag/tamthuc_rag/guard.py
  - packages/tamthuc_rag/tamthuc_rag/disclosure.py
  - packages/tamthuc_rag/tests/test_interpret.py
  - docs/contracts/interpretation.schema.json
---

## §1 - Description (BCP-14 normative)

This is the interpretation core: it reads a la so envelope plus the passages TASK-RAG-002 retrieved, builds a grounded prompt, calls an LLM, and returns a structured, cited interpretation. It is where the "AI does not invent numbers, and does not assert beyond its sources" principle is enforced (Claude-06 s4.1, s4.3; strategy 4.4). The module SHALL read the la so envelope (TASK-PLAT-002) read-only and SHALL NEVER write `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai`; it only interprets what the deterministic engine produced (strategy 4.3).

The output SHALL be a single structured object: `beginner_interpretation`, `expert_interpretation`, `recommendations[]`, `citations[]` (citation cards), and `confidence`, validated against `docs/contracts/interpretation.schema.json`. The prompt SHALL be assembled as system prompt + retrieved context + chart summary + detected patterns + persona level (beginner | expert), matching step 6 of the query flow (strategy 4.2). The LLM caller SHALL request structured output and SHALL reject/repair a response that is not schema-valid.

Anti-hallucination SHALL be enforced in three layers (Claude-06 s4.3): (1) citation-required - every asserted claim maps to at least one retrieved `citation_id`, and an output with unsupported claims is rejected or has those claims stripped; (2) retrieval-only - the model is instructed to interpret only the supplied passages and not free memory, and every `citation_id` it emits SHALL exist in the retrieved set (a fabricated citation fails validation); (3) human-in-the-loop - the output SHALL carry a `requires_human_review` flag and, per TASK-RAG-004, important judgments pass a HumanReviewGate before reaching the user. Every output SHALL carry AIDisclosure metadata marking it AI-generated, and citations SHALL be returned as cards (Han + bạch thoại + dịch + locator) for the UI (TASK-WEB-003). No output SHALL contain medical, legal, or financial advice framed as a divination verdict (strategy 7, TASK-LEGAL-003).

## §2 - Why this design (rationale for humans)

This task is where the product earns trust or loses it. A language model asked to interpret a chart from free memory will produce fluent text that mixes real tradition with invention, and a user cannot tell which is which (Claude-06 s4.3). For a heritage subject that is both a knowledge error and a trust harm, and under VN law it is exactly the failure mode that turns "heritage education" into "superstition for profit" (strategy 7, RISK-4). The three anti-hallucination layers convert interpretation from free judgment into a traceable, sourced statement: no claim without a citation, no citation the retriever did not supply, and a human in the loop for anything consequential. The AIDisclosure label and the citation cards are the same discipline made visible in the interface (strategy 4.4).

The structured output with paired beginner and expert readings serves the two-audience product without two prompts fighting each other: the same grounded context yields a plain-language reading and a technically precise one, and both cite the same passages. The read-only rule against the engine fields is not a nicety - it is the architectural boundary (strategy 4.3). The moment the interpretation branch can write `cach_cuc` or `ban`, determinism is gone and the chart is no longer reproducible from its inputs and flags. Keeping this module a pure reader of the envelope is what preserves the split the whole platform rests on.

## §3 - Contract (prompt library, LLM caller, output schema, guard)

### Output schema (`tamthuc_rag/schema.py` + `docs/contracts/interpretation.schema.json`)

```python
class CitationCard(BaseModel):
    citation_id: str
    source: str
    unit_type: str
    han: str | None
    bach_thoai: str | None
    dich: str | None
    locator: str | None            # dieu/khoa number or range for display

class Recommendation(BaseModel):
    text: str
    rationale: str
    citations: list[str]           # citation_ids, each must exist in the retrieved set

class AIDisclosure(BaseModel):
    is_ai_generated: bool = True
    model: str
    prompt_version: str
    retrieved_citation_ids: list[str]
    generated_at: datetime
    review_status: Literal["pending", "not_required", "approved", "rejected"] = "pending"

class Interpretation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    persona_level: Literal["beginner", "expert"]
    beginner_interpretation: str
    expert_interpretation: str
    recommendations: list[Recommendation]
    citations: list[CitationCard]
    confidence: float              # 0..1
    requires_human_review: bool
    disclosure: AIDisclosure
```

### Prompt library and builder (`prompts/`, `prompt_builder.py`)

`system.md` fixes the role and the hard rules; `beginner.md` / `expert.md` shape tone and depth per persona. The builder assembles the LLM messages:

```
build_messages(la_so, retrieval_result, persona) ->
  [ system  = prompts/system.md,
    user    = chart_summary(la_so)            # he, key ban components, cach_cuc + meanings, co_truong_phai flags
            + detected_patterns(la_so.cach_cuc)
            + retrieved_context(retrieval_result)   # numbered passages with citation_ids, 3 layers
            + persona_instructions(persona)
            + output_contract ]                 # "return only JSON matching the Interpretation schema"
```

`system.md` skeleton (the load-bearing rules, verbatim intent):

```
You are an interpreter of Tam Thuc (LiuRen / QiMen / TaiYi) charts for a heritage-education
and decision-support product. You do not cast or recompute charts; the chart is given.
Rules you must follow:
1. Interpret ONLY from the numbered passages provided below. Do not use outside memory of these texts.
2. Every claim must cite at least one passage by its citation_id. If the passages do not support a
   claim, do not make it; say the sources are insufficient instead.
3. Only cite citation_ids that appear in the provided passages. Never invent a citation.
4. Frame everything as decision-support and heritage knowledge, never as a certain future event.
   Give no medical, legal, or financial verdict.
5. Return ONLY a JSON object matching the Interpretation schema. No prose outside the JSON.
```

### LLM caller (`tamthuc_rag/llm.py`)

```python
class LLM(Protocol):
    name: str
    def complete(self, messages: list[dict], schema: type[BaseModel]) -> BaseModel: ...

class StructuredLLM:
    # provider-abstracted (OpenAI/Anthropic/local); JSON/function-call structured output at low
    # temperature; on invalid JSON, one repair retry, then raise. TASK-RAG-007 wraps this with
    # circuit-breaker + fallback + rule-based degradation.
    ...
```

### Anti-hallucination guard (`tamthuc_rag/guard.py`)

```python
def enforce(interp: Interpretation, retrieved: RetrievalResult) -> Interpretation:
    allowed = {c.citation_id for c in retrieved.chunks}
    # (2) retrieval-only: every cited id must be in `allowed`; a fabricated id -> reject
    # (1) citation-required: every recommendation and each interpretation claim maps to >=1 allowed id;
    #     drop or reject unsupported claims per policy
    # (3) HITL: set requires_human_review from confidence threshold + question-stakes policy
    # attach/refresh AIDisclosure(model, prompt_version, retrieved_citation_ids, generated_at)
    ...
```

`disclosure.py` builds the `AIDisclosure` and the citation cards from the retrieved passages, so the label and the cards are always present and always reflect the actual grounding.

### interpret() entry point (`tamthuc_rag/interpret.py`)

```python
def interpret(la_so: LaSo, request: RetrievalRequest, persona: str,
              retriever: HybridRetriever, llm: LLM) -> Interpretation:
    retrieved = retriever.retrieve(request)          # TASK-RAG-002 (read chart context)
    if not retrieved.chunks:                          # empty grounding -> no free-memory claim
        return insufficient_sources(la_so, persona, retrieved)
    messages = build_messages(la_so, retrieved, persona)
    raw = llm.complete(messages, Interpretation)
    return enforce(raw, retrieved)                     # 3-layer guard + disclosure + cards
```

`interpret` treats `la_so` as read-only throughout; a post-condition test asserts the envelope is byte-identical before and after.

## §4 - Acceptance criteria

1. `interpret` returns a schema-valid `Interpretation` with both persona readings, recommendations, citation cards, a confidence, `requires_human_review`, and AIDisclosure populated.
2. Retrieval-only guard: an LLM response citing a `citation_id` not in the retrieved set is rejected (or that claim stripped) - a fabricated citation never reaches output.
3. Citation-required guard: a recommendation with an empty `citations` list is dropped or the output is rejected per policy; no surviving claim is uncited.
4. Empty retrieval yields an "insufficient sources" interpretation (no confident claims), not a free-memory answer.
5. AIDisclosure is present on every output with `is_ai_generated=true`, `model`, `prompt_version`, and the exact `retrieved_citation_ids`; citation cards carry the three text layers and a locator.
6. The input la so envelope is unchanged after `interpret` (read-only invariant asserted by a byte-equality test); no code path writes `ban`/`cach_cuc`/`lich_phap`/`co_truong_phai`.
7. No output contains a medical/legal/financial verdict on a policy test set of adversarial questions (framing guard, aligned with TASK-LEGAL-003).

## §5 - Verification

- `tests/test_interpret.py`: full `interpret` with a stub `LLM` returning canned structured outputs (good, fabricated-citation, uncited-recommendation, empty-retrieval, and advice-verdict cases) plus the TASK-RAG-002 stub retriever; asserts each guard fires; asserts the read-only envelope invariant; asserts AIDisclosure/citation-card completeness.
- Schema: `docs/contracts/interpretation.schema.json` validates every good output and rejects malformed ones; the Pydantic model and the JSON Schema are checked for parity in CI.
- Prompt snapshot: `build_messages` output is snapshot-tested so a prompt change is a reviewed diff carrying a bumped `prompt_version`.
- The measurable-quality gate (faithfulness/relevance/citation accuracy) is TASK-RAG-006's eval loop; this task provides the hooks (`prompt_version`, `retrieved_citation_ids`) it scores against.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_rag`, `pytest packages/tamthuc_rag`.

## §6 - Implementation skeleton

1. `schema.py` + `docs/contracts/interpretation.schema.json`: the output contract (source of truth).
2. `prompts/`: `system.md` (the five rules), `beginner.md`, `expert.md`; version them (`prompt_version`).
3. `prompt_builder.py`: `build_messages`, `chart_summary`, `detected_patterns`, `retrieved_context` (numbered, citation-tagged, 3-layer).
4. `llm.py`: the `LLM` protocol and `StructuredLLM` (structured output, low temperature, one repair retry).
5. `guard.py` + `disclosure.py`: the three-layer `enforce`, the `AIDisclosure`/citation-card builders.
6. `interpret.py`: the entry point with the empty-retrieval path and the read-only invariant.

## §7 - Dependencies

Depends on TASK-RAG-002 (the grounded passages it interprets) and TASK-PLAT-002 (the la so envelope it reads). Blocks the AI-facing product: TASK-RAG-004 (HumanReviewGate consumes `requires_human_review` and the AIDisclosure), TASK-RAG-006 (eval loop scores this output), TASK-RAG-007 (fallback wraps the LLM caller), TASK-WEB-003 (results screen renders the interpretation + citation cards + AIDisclosure), TASK-REPORT-001 (report assembly), and TASK-STRAT-003 (chu-khach framework builds on interpretation).

## §8 - Example payloads

```json
// Interpretation (abbreviated)
{ "persona_level": "beginner",
  "beginner_interpretation": "The chart shows a favorable window for initiating... [yba_dieu_012].",
  "expert_interpretation": "Binh gia truc phu on cung 1 with Sinh mon under zhuan-ban forms Thanh Long Hoi Dau... [yba_dieu_012].",
  "recommendations": [ { "text": "Treat the near-term as a supportive window to begin, not to wait.",
      "rationale": "Cat cach cuc on the acting palace.", "citations": ["yba_dieu_012"] } ],
  "citations": [ { "citation_id": "yba_dieu_012", "source": "yen_ba_dieu_tau_ca", "unit_type": "dieu",
      "han": "丙加值符...", "bach_thoai": "...", "dich": "Binh gia truc phu...", "locator": "dieu 12" } ],
  "confidence": 0.72, "requires_human_review": false,
  "disclosure": { "is_ai_generated": true, "model": "gpt-4o-mini", "prompt_version": "sys-1.0.0",
    "retrieved_citation_ids": ["yba_dieu_012"], "generated_at": "2026-07-08T12:00:00Z",
    "review_status": "not_required" } }
```

## §9 - Open questions

- Claim-to-citation mapping granularity: sentence-level attribution vs paragraph-level. Default: require each `recommendation` and each interpretation paragraph to carry >=1 citation; sentence-level attribution is a TASK-RAG-006 quality refinement, not a P0 blocker.
- The `requires_human_review` policy (confidence threshold, high-stakes question types). Default: a conservative threshold plus a question-type allowlist; the actual gate and queue are TASK-RAG-004. Tune from review outcomes.
- Persona handling: two fields in one call (as here) vs two calls. Default: one grounded call returning both readings (shared context, cheaper, guaranteed same citations); revisit if quality of one persona suffers.
- Term-sense expansion of the query (bản nghĩa / dẫn thân / giả tá / điển tích) is TASK-RAG-005 and widens retrieval upstream of this task; not in P0 scope here.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Fabricated citation | LLM emits a citation_id not retrieved | `enforce` rejects it (id not in `allowed`); output repaired or rejected, never shipped |
| Uncited claim | a recommendation/paragraph with no citation | dropped or whole output rejected per policy; nothing uncited survives |
| Free-memory answer | empty retrieval but model answers anyway | empty-retrieval path returns "insufficient sources"; guard blocks confident uncited claims |
| Engine field write | interpretation mutates cach_cuc/ban | impossible: la so read-only; post-condition byte-equality test; no setter called |
| Advice verdict | model gives medical/legal/financial ruling | framing guard + system rule 4; policy test set; blocked (TASK-LEGAL-003) |
| Missing disclosure | output without AIDisclosure | `disclosure.py` always attaches it; schema requires it; missing -> validation fails |
| Invalid JSON | model returns prose or bad JSON | one repair retry, then raise; TASK-RAG-007 provides fallback/degradation |

## §11 - Notes

This task is the responsible-AI heart of the product and the reason the deterministic/AI split exists at all. Two invariants are non-negotiable: it reads the la so and never writes it, and it makes no claim without a retrieved citation. The eval loop (TASK-RAG-006) turns those invariants into a measured gate (faithfulness, relevance, citation accuracy - RISK-3, RISK-9); the HumanReviewGate (TASK-RAG-004) puts a person behind the important calls; the fallback (TASK-RAG-007) keeps a graceful degradation when the LLM is unavailable. Keep the prompt library versioned - a change to `system.md` is a change to the product's safety posture and must ship as a reviewed diff with a bumped `prompt_version`.
