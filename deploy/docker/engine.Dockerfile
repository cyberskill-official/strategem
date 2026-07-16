# TASK-PLAT-004: Rust engine service (deterministic branch)
FROM rust:1.85-bookworm AS build
WORKDIR /src
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates ./crates
# smoke must produce a binary (src/main.rs); --bins avoids rlib-only installs
RUN cargo build --release -p smoke --bins \
  && test -x /src/target/release/smoke

FROM debian:bookworm-slim AS runtime
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
# Placeholder binary until dedicated engine service crate lands.
COPY --from=build /src/target/release/smoke /app/engine
USER nobody
ENTRYPOINT ["/app/engine"]
