# edge-case-matrix@1 — COV-011

| id | category | case | expected | test |
|----|----------|------|----------|------|
| E1 | CONFIG | INTERPRET_MODE=template | template | test_interpret_mode_explicit_template |
| E2 | CONFIG | INTERPRET_MODE=rag | rag | test_interpret_mode_explicit_rag |
| E3 | DISCLOSURE | template badge | is_ai_generated false / mode_badge | test_template_mode_badge_no_fake_rag |
| E4 | CITATION | rag with patterns | layers or locator | test_rag_mode_requires_citation_layers |
| E5 | SECURITY | rag empty sources | refuse free-form | test_refuse_when_no_sources_rag |
| E6 | REVIEW | medical category | human review gate | test_restricted_category_triggers_gate |
| E7 | REGRESSION | interpret happy path | citations kept | test_interpret_happy_path_and_readonly |
| E8 | DEGRADATION | empty retrieval | confidence 0 + review | test_empty_retrieval |
