# FR-PLAT-004: Python API / auth / RAG surface
FROM python:3.12-slim-bookworm AS build
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /src
COPY pyproject.toml uv.lock ./
COPY packages ./packages
RUN uv sync --all-packages --frozen || uv sync --all-packages

FROM python:3.12-slim-bookworm AS runtime
# Security patches for OS packages scanned by Trivy in CD.
RUN apt-get update \
  && apt-get upgrade -y --no-install-recommends \
  && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /src/.venv /app/.venv
COPY packages ./packages
COPY docs ./docs
COPY db ./db
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/packages
USER nobody
# API app binary lands with FR-API-001; image validates package install path.
CMD ["python", "-c", "import tamthuc_auth, db_schema; print('api-image-ok')"]
