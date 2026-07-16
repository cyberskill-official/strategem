# Resilience policy (TASK-PLAT-008)

| Control | Default |
|---|---|
| Circuit failure threshold | 3 |
| Circuit cooldown | 30s |
| Retry max attempts | 3 |
| Backoff | exponential + jitter |
| Non-retry | HTTP 4xx / PermanentError |
| Multi-engine | partial success + degraded list |
| LLM down | rule-based interpretation + AIDisclosure.fallback |
