# docs/contracts/

Cross-language contracts for Tam Thuc Strategem.

Owned by PLAT. The single source of truth for shared shapes is here (JSON Schema preferred), with generated or hand-written types in the consuming languages.

Current:
- (TASK-PLAT-002) laso-envelope.schema.json — the la so JSON envelope (strategy 4.3). Every engine emits it exactly; the Python interpretation branch consumes it read-only.

Do not edit shapes in language-specific files without updating the contract here and the version. Contract drift fails CI (see PLAT-002).