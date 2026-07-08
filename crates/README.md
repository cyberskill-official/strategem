# crates/

Rust crates for Tam Thuc Strategem.

Per DEC-2 (strategy 3.2): deterministic engines, rule detection, and the la-so envelope live here under a Cargo workspace.

- `smoke/` - placeholder so the CI lane has a buildable/testable member from PLAT-001. Will be removed or replaced by real crates (cyberos-lichphap from CORE-001, laso-envelope from PLAT-002, etc.).

Member crates are added by their owning FRs. Every crate participates in:
- `cargo fmt --check`
- `cargo clippy --workspace -- -D warnings`
- `cargo test --workspace`

See root `Cargo.toml`, `rust-toolchain.toml`, and `.github/workflows/ci.yml`.