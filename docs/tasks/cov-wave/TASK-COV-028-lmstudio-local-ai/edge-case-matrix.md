# edge-case-matrix@1 — COV-028

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | CONTRACT | Mock chat.completions → interpret shape | beginner/expert/recommendations | test_openai_compatible_chat_completions_contract |
| E2 | DEGRADATION | Unreachable base URL | RuntimeError llm_unreachable/timeout | test_openai_compatible_unreachable |
| E3 | CONFIG | LLM_BACKEND unset | StubLlm default (CI safe) | test_llm_from_env_stub_default |
| E4 | CONFIG | LLM_BACKEND=lmstudio\|openai_compatible | OpenAICompatibleLlm | test_llm_from_env_openai |
| E5 | DEGRADATION | Host LMStudio down | interpret uses template + honest disclosure | live probe + interpret path |
| E6 | SECURITY | No cloud key required for local | empty API key ok | OpenAICompatibleLlm + docs |
| E7 | NETWORK | Docker → host LMStudio | host.docker.internal in compose | docker-compose.local.yml |
| E8 | DOCS | Env table + load model steps | local-docker-lmstudio.md | test_local_runbook_exists |
