---
id: COV-011
title: "Production RAG default interpretation path (or honest template mode flag)"
module: RAG
status: done
class: product
priority: MUST
phase: P1
lang: python
effort_h: 24
depends_on: ['RAG-001', 'RAG-002', 'RAG-003', 'KB-003']
refs: ['Claude-06 s4', 'Grok-32', 'benchmark-claude §2 RAG', 'benchmark-grok Epic4']
created: 2026-07-13
source: coverage-to-100-benchmarks
---

# COV-011 — Production RAG default interpretation path (or honest template mode flag)

## Goal

Default interpretation is retrieval-grounded when configured; otherwise explicit template mode badge.

Closes residual gaps from:
- `docs/strategy/claude-docs-coverage-benchmark-2026-07-13.md`
- `docs/strategy/grok-docs-coverage-benchmark-2026-07-13.md`

Existing module FRs marked `done` at package level may already implement partial surfaces; this FR is the **product + acceptance** completion gate for 100% score on those dimensions.

## §1 Acceptance criteria (normative)

1. MUST set INTERPRET_MODE=rag|template; default rag when vector store available.
2. RAG mode MUST attach ≥1 citation with triple-layer locator when corpus present.
3. Template mode MUST show engine badge equivalent (no fake RAG claims).
4. HumanReviewGate MUST apply for restricted categories.
5. Tests for both modes + anti-hallucination refuse when no sources.

## §2 Non-goals

- No destiny / prophecy claims (VOICE.md).
- No multi-payment-provider sprawl unless this is COV-026 (single rail only).
- Do not re-open CyberSkill DS for Grok navy mockups.

## §3 Verification

- Unit/integration tests named in implementation.
- Update coverage scores in strategy benchmarks when done (human sets FR `done` only after HITL).
- `bash .cyberos/cuo/gates/run-gates.sh` green where applicable.

## §4 Dependencies

depends_on: RAG-001, RAG-002, RAG-003, KB-003

## §5 Refs

Claude-06 s4, Grok-32, benchmark-claude §2 RAG, benchmark-grok Epic4
