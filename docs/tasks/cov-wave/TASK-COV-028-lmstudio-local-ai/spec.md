---
id: COV-028
title: "LMStudio local AI — OpenAI-compatible LLM client + honest degraded path"
module: RAG
status: done
class: product
priority: MUST
phase: P0
lang: python
effort_h: 16
depends_on: ['RAG-003', 'RAG-007', 'COV-011']
refs: ['enterprise-local-objective', 'Claude-06 s4', 'Grok-32', 'benchmark-claude §2 RAG']
created: 2026-07-13
source: enterprise-local-docker-lmstudio-objective
---

# COV-028 — LMStudio local AI — OpenAI-compatible LLM client + honest degraded path

## Goal

Interpretation/RAG uses a **configurable OpenAI-compatible HTTP client** whose default local profile targets **LMStudio** (`http://127.0.0.1:1234/v1` or compose `host.docker.internal:1234`) with a selectable model id — no cloud API key required for the local path. When LMStudio is down, the product MUST fall back to the existing template/degraded path with an honest badge (no fake RAG/LLM claims).

Closes residual gaps from:
- Enterprise OBJECTIVE: fully worked locally with LMStudio as local AI
- Today `tamthuc_rag.llm` only ships `StubLlm` (CI); no OpenAI-compatible production client
- Dual-benchmark RAG dimensions need a real local AI entry for enterprise claims

## §1 Acceptance criteria (normative)

1. MUST implement `OpenAICompatibleLlm` (or equivalent name) in `packages/tamthuc_rag` implementing the existing `LlmClient` protocol (`complete(prompt) -> dict` with beginner/expert/recommendations shape).
2. MUST configure via env (names documented): base URL (default `http://127.0.0.1:1234/v1`), model id, optional API key header (`LM_API_KEY` / `OPENAI_API_KEY` — empty ok for LMStudio), timeout, and enable flag (`LLM_BACKEND=openai_compatible|stub|off`).
3. MUST call OpenAI-compatible `POST {base}/chat/completions` (or documented equivalent) and parse structured JSON from the model (repair/reject invalid schema per RAG-003 guard).
4. MUST wire factory used by interpret/orchestrator so production API path can select LMStudio without code edits.
5. MUST preserve degraded/template path when backend unreachable or circuit open (`RAG-007`); disclosure/badge MUST NOT claim live LLM when stub/template used.
6. MUST document LMStudio load model + base URL + Docker `extra_hosts: host.docker.internal:host-gateway` in `docs/deploy/local-docker-lmstudio.md`.
7. MUST unit-test client against a local HTTP mock (contract); optional live dual-run when LMStudio is up. Capture logs or honest probe-failure + mock evidence under operator scratch.
8. MUST NOT require cloud OpenAI as the default for local enterprise path.

## §2 Non-goals

- Shipping or containerizing LMStudio itself.
- Multi-provider router sprawl (one OpenAI-compatible adapter is enough; cloud is optional same client).
- Replacing anti-hallucination / HumanReviewGate (RAG-003/004).

## §3 Verification

- Unit tests: mock server returns chat.completions → structured interpret dict; timeout/connection → raises or triggers degraded.
- Docs + env sample present.
- When LMStudio running: two interpretation calls succeed with model disclosure; when not: degraded path honest.
- `bash .cyberos/cuo/gates/run-gates.sh` green for Python lane changes.
- Human sets task `done` only after HITL.

## §4 Dependencies

depends_on: RAG-003, RAG-007, COV-011 (product default path; client can land first)

Note: Implementation MAY land the client before COV-011 product default flip; COV-011 remains the productization gate for default rag|template mode.

## §5 Refs

enterprise-local-objective, Claude-06 s4, Grok-32, benchmark-claude §2 RAG
