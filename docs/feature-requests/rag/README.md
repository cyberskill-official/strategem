# RAG - AI interpretation

The interpretation branch: it takes the la so the deterministic engine cast and produces a cited, structured reading of it. This is the right-hand branch of the core (strategy 4.1) - knowledge ingestion, hybrid retrieval, and grounded LLM interpretation - joined to the engine branch only through the la so JSON envelope. Language is Python / FastAPI (DEC-2); everything lives in one package, `tamthuc_rag`. Primary sources: Claude 06 s3-4 (knowledge graph, RAG on classical text, anti-hallucination), Grok 23 (prompts), Grok 32 (RAG service). See the unified plan sections 4.1-4.4, 7, and 8.

The one hard rule of this module: the interpretation branch never casts or recomputes a chart. It reads `he`, `ban`, `cach_cuc`, `lich_phap`, and `co_truong_phai`, and it never writes them (strategy 4.3). Every number and position comes from the deterministic engine; the AI only interprets, grounded in retrieved text, cited, and labeled.

## FRs

| FR | Pri | Phase | h | depends_on | Spec | Title |
|---|---|---|--:|---|---|---|
| RAG-001 | MUST | P0 | 14 | KB-003, PLAT-001 | [FR-RAG-001](FR-RAG-001-ingest-embed.md) | Classical-text ingest + multilingual embedding + vector store |
| RAG-002 | MUST | P0 | 12 | RAG-001, KB-005 | [FR-RAG-002](FR-RAG-002-hybrid-retriever.md) | Hybrid retriever (vector + graph, top-k, per-system filter) |
| RAG-003 | MUST | P0 | 16 | RAG-002 | [FR-RAG-003](FR-RAG-003-interpret-llm.md) | Prompt library + LLM caller + structured output + anti-hallucination + AIDisclosure |
| RAG-004 | MUST | P1 | 12 | RAG-003 | [FR-RAG-004](FR-RAG-004-human-review-gate.md) | HumanReviewGate pipeline (queue, approve/reject, audit) |
| RAG-005 | SHOULD | P2 | 10 | RAG-002 | [FR-RAG-005](FR-RAG-005-term-sense.md) | Term-sense expansion (ban nghia / dan than / gia ta / dien tich) |
| RAG-006 | MUST | P2 | 12 | RAG-003, KB-002 | [FR-RAG-006](FR-RAG-006-eval-loop.md) | Interpretation eval loop (faithfulness/relevance/citation) + CI gate |
| RAG-007 | MUST | P1 | 8 | RAG-003 | [FR-RAG-007](FR-RAG-007-fallback.md) | LLM fallback + circuit breaker + rule-based degradation |

Three P0 FRs are authored (RAG-001..003, the ingest -> retrieve -> interpret spine). Four are authored: RAG-004 (HumanReviewGate, P1), RAG-005 (term-sense expansion of văn ngôn văn queries - bản nghĩa / dẫn thân / giả tá / điển tích, P2), RAG-006 (the interpretation eval loop + CI gate, P2), and RAG-007 (LLM fallback / circuit breaker / rule-based degradation, P1).

## Internal spine

```
RAG-001 (ingest classical text -> 3-layer chunks -> multilingual embed -> vector store)
   -> RAG-002 (hybrid retrieve: vector + KB-005 graph, per-system filter, fused chunks + citations)
        -> RAG-003 (prompt + LLM + structured {beginner/expert/recs/citations/confidence}
                    + 3-layer anti-hallucination + AIDisclosure + citation cards)
             -> RAG-004 (HumanReviewGate)   -> RAG-006 (eval loop + CI gate)
             -> RAG-007 (fallback / degradation)
        -> RAG-005 (term-sense query expansion)
```

## Cross-module dependencies

- Depends on KB: KB-003 (the three-layer classical-text store RAG-001 ingests) and KB-005 (the knowledge-graph query API that is RAG-002's graph arm). Depends on PLAT: PLAT-001 (Python workspace), PLAT-002 (the la so envelope RAG-003 reads), and PLAT-003 (Postgres/pgvector for the default vector store). Fed by KB-002 (the seeded patterns whose meanings and citations enrich the chart summary and the eval set).
- Blocks WEB-003 (the results screen renders the interpretation + citation cards + AIDisclosure), REPORT-001 (structured report assembly), and STRAT-003 (the chu-khach decision framework builds on interpretation). RAG-003 is the specific blocker for all three.
- Phase-sequencing flag: RAG-002 is P0 but its `depends_on` includes KB-005, which is P2. RAG-002 ships the vector arm as the hard P0 requirement and treats the graph arm as an optional runtime capability that activates when KB-005 lands, degrading to vector-only until then. The backlog should either schedule the vector-only slice in P0 and the graph-arm activation in P2, or pull KB-005 forward. See FR-RAG-002 section 9.

## Module notes

- The interpretation branch never re-computes a chart and never writes `ban`, `cach_cuc`, `lich_phap`, or `co_truong_phai` (strategy 4.3). It reads the la so envelope and interprets it; the read-only invariant is asserted by a byte-equality test in FR-RAG-003. This is the architectural boundary the whole platform rests on - the moment the AI can write an engine field, determinism and reproducibility are gone.
- Every output is retrieval-grounded, cited, and AIDisclosure-labeled. Three anti-hallucination layers enforce it (Claude-06 s4.3): citation-required (no source, no claim), retrieval-only (interpret only supplied passages; a fabricated citation fails validation), and human-in-the-loop. Citations are returned as cards (Han + bạch thoại + dịch + locator) for the UI, and the AIDisclosure label marks every output AI-generated. No output gives a medical, legal, or financial verdict (strategy 7, FR-LEGAL-003).
- Important judgments pass a HumanReviewGate. FR-RAG-003 emits `requires_human_review` and the AIDisclosure `review_status`; FR-RAG-004 implements the queue, approve/reject, and audit trail before such a reading reaches a user.
- The eval loop scores faithfulness, relevance, and citation accuracy against a validation set of classical cases (FR-RAG-006), as a CI gate so interpretation-quality regressions do not ship silently (RISK-3, RISK-9). FR-RAG-003 provides the hooks it scores against: a versioned `prompt_version` and the exact `retrieved_citation_ids` on every output.
