# KB - knowledge base and graph

The structured-knowledge layer of the interpretation branch: the graph of the three systems' primitives and relations, the 150-200 cited interpretation patterns, the three-layer classical-text store, the curation workflow, and the hybrid-retrieval query API. It is the source of truth the deterministic engines read for relations and the RAG branch retrieves from for meaning - one half of hybrid retrieval, joined to the vector arm in FR-RAG-002. Language is Python (DEC-2); everything lives in one package, `tamthuc_kb`. Primary sources: Claude 06 s3 (knowledge graph, RAG on classical text), Grok 37 (pattern seeding), Grok 24 (curation). See the unified plan sections 4.1, 5, and RISK-9.

## FRs

| FR | Pri | Phase | h | Title |
|---|---|---|--:|---|
| KB-001 | SHOULD | P0 | 12 | [Knowledge-graph schema (node + edge taxonomy) + storage](FR-KB-001-knowledge-graph/spec.md) |
| KB-002 | MUST | P0 | 16 | [Pattern seeding (150-200 patterns, 3 systems, JSON conditions + citations)](FR-KB-002-pattern-seeding/spec.md) |
| KB-003 | MUST | P1 | 12 | Classical-text three-layer store (Han/bach thoai/dich) + chunking |
| KB-004 | SHOULD | P2 | 10 | KB curation workflow + expert review + versioning |
| KB-005 | SHOULD | P2 | 12 | Knowledge-graph hybrid-retrieval query API |

Two P0 FRs are authored (KB-001 the graph schema, KB-002 the pattern seed). Three are authored: KB-003 (the three-layer classical-text store RAG-001 ingests, P1), KB-004 (the expert-review and versioning workflow over the seeded patterns, P2), and KB-005 (the graph query API that is RAG-002's graph arm, P2).

## Internal spine

```
KB-001 (node + edge taxonomy + pluggable GraphStore, default relational l2_edge)
   -> KB-002 (150-200 cited patterns per the RULE-001 schema; doubles as the RISK-9 validation set)
        -> KB-004 (curation, expert sign-off, versioning; P2)
   -> KB-005 (graph hybrid-retrieval query API; P2)  [needs KB-003]
KB-003 (three-layer classical-text store + chunking; P1)  -> RAG-001 ingest, KB-005
```

## Cross-module dependencies

- Depends on PLAT-001 (the Python workspace; KB-001 and KB-003 root here). Soft edge to PLAT-003 for the shared Postgres that hosts the `l2_node` / `l2_edge` graph tables (DDL owned in KB-001) and the `knowledge_patterns` table (shape owned in RULE-001, filled by KB-002).
- Depends on RULE: KB-002 fills the pattern-as-data shape and seed-file format that FR-RULE-001 owns, validated against the FR-RULE-002 DSL. The seed is the ruleset FR-RULE-003 serves to the engines.
- Blocks RAG: KB-003 is what FR-RAG-001 ingests and embeds; KB-005 is the graph arm FR-RAG-002 fuses with the vector arm; KB-002's cited patterns enrich the FR-RAG-003 chart summary and are the FR-RAG-006 eval corpus (RISK-9). Citations on every pattern resolve into the KB-003 corpus.
- Feeds the engines: the ngu hanh / dia chi relations in the KB-001 graph are the reference the deterministic relation logic (FR-CORE-007, FR-RULE-002) reads, so "what relates to what" has one source.

## Module notes

- One package, one installable unit. All five FRs live in and extend `tamthuc_kb` (graph, seed, corpus, curation, query modules), so the knowledge base is one mypy-clean, pytest-covered Python package, not five scattered pieces.
- The graph is relational at MVP. The default `GraphStore` is a relational edge table `l2_edge(src, rel, dst)` plus `l2_node` in the shared Postgres, matching the cyberos house pattern - no separate graph database is introduced at MVP. Neo4j, RDF, and property-graph adapters are reserved behind the same protocol. Node kinds and edge relations are closed enums; a free-text kind or relation is rejected, not stored.
- Patterns are data, and every active pattern is cited. KB-002 authors 150-200 rows against the RULE-001 schema; no `active` pattern ships without a citation, because no source means no claim under the anti-hallucination rule (strategy 4.4). The same rows are the RISK-9 interpretation-quality validation dataset, so the ruleset and the test set cannot drift - they are one artifact.
- Content is presented as heritage, fairly and in the original. Classical text is stored in three parallel layers (nguyen van chu Han / ban bach thoai / ban dich) and chunked by natural bibliographic unit (dieu / phap / khoa / cau), never by token window, so a citation points at a whole thought and returns the Han alongside its translation. Where schools read a pattern differently, the difference is recorded, not silently resolved (strategy 7).
- QiMen carries the P0 weight. Per DEC-4 and RISK-7, the P0 seed is QiMen-heavy (the flagship, the most school-variant-heavy system); LiuRen and TaiYi are seeded representatively now and grow in P1/P2.
