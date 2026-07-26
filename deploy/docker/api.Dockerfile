# COV-027: Python API + cast-cli for local/full product casts
# Stage 1 — Rust cast-cli
FROM rust:1.85-bookworm AS rust-build
WORKDIR /src
COPY Cargo.toml Cargo.lock rust-toolchain.toml ./
COPY crates ./crates
RUN cargo build --release -p cast-cli --bins \
  && test -x /src/target/release/cast-cli

# Stage 2 — Python deps (editable install paths point at /src/packages/.../src)
FROM python:3.12-slim-bookworm AS py-build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /src
COPY pyproject.toml uv.lock ./
COPY packages ./packages
RUN uv sync --all-packages --frozen || uv sync --all-packages

# Stage 3 — runtime MUST keep /src tree so editable .pth files resolve
FROM python:3.12-slim-bookworm AS runtime
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && apt-get install -y --no-install-recommends ca-certificates \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY --from=py-build /src/.venv /src/.venv
COPY packages ./packages
COPY docs ./docs
COPY db ./db
# Pattern seeds + classical corpus units (KB/RAG product surfaces)
COPY data ./data
COPY --from=rust-build /src/target/release/cast-cli /src/cast-cli
ENV PATH="/src/.venv/bin:$PATH"
ENV CAST_CLI=/src/cast-cli
ENV HOST=0.0.0.0
ENV PORT=8000
EXPOSE 8000
RUN useradd --create-home --uid 10001 appuser \
  && chown -R appuser:appuser /src
USER appuser
CMD ["python", "-m", "tamthuc_api"]
