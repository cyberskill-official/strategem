# laso-envelope

Pydantic v2 models for the Tam Thuc la so JSON envelope (PLAT-002).

- Single source of truth: `docs/contracts/laso-envelope.schema.json`
- Mirrors the Rust `laso-envelope` crate types.
- `extra="forbid"` on models so unknown fields are rejected.
- Cross-language round-trip and cache-key contract tests live alongside the fixtures.

This package is part of the hybrid workspace boundary contract. Engines emit; interpretation consumes read-only.
