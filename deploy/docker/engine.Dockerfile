# FR-PLAT-004: Rust engine service (deterministic branch)
FROM rust:1.85-bookworm AS build
WORKDIR /src
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates ./crates
RUN cargo build --release -p smoke || cargo build --release --workspace

FROM debian:bookworm-slim AS runtime
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Placeholder binary until engine service crate lands; smoke proves the multi-stage path.
COPY --from=build /src/target/release/smoke /app/engine
USER nobody
ENTRYPOINT ["/app/engine"]
