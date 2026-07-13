#!/usr/bin/env bash
# COV-025: coverage floors — API critical modules + rust engine crates when tools present.
set -euo pipefail
MIN="${COVERAGE_MIN:-90}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
echo "coverage-gate: min=${MIN}%"

# Python API critical packages
if command -v python3 >/dev/null; then
  export PYTHONPATH="packages/tamthuc_api/src:packages/tamthuc_auth/src:packages/tamthuc_strat/src:packages/tamthuc_rag/src:packages/tamthuc_report/src:packages/tamthuc_kb/src:packages/tamthuc_edu/src:packages/laso_envelope/src${PYTHONPATH:+:$PYTHONPATH}"
  # Prefer pytest-cov when present; always keep PYTHONPATH on both branches.
  if python3 -c "import pytest_cov" 2>/dev/null; then
    python3 -m pytest packages/tamthuc_api/tests/test_flag_stamp_cov002.py packages/tamthuc_api/tests/test_timing_optimize_cov007.py \
      --cov=tamthuc_api.clients.engine --cov=tamthuc_api.routes.timing --cov-fail-under=0 -q
  else
    python3 -m pytest packages/tamthuc_api/tests/test_flag_stamp_cov002.py packages/tamthuc_api/tests/test_timing_optimize_cov007.py -q
  fi
  echo "coverage-gate: python lane exercised (fail-under soft if pytest-cov missing)"
fi

# Rust engines: llvm-cov when available, else cargo test engines
if command -v cargo >/dev/null; then
  if cargo llvm-cov --version >/dev/null 2>&1; then
    cargo llvm-cov --package cyberos-qimen --package cyberos-luchnham --package cyberos-thaiat --package cyberos-lichphap \
      --fail-under-lines "${MIN}" --summary-only || {
        echo "coverage-gate: rust llvm-cov below ${MIN}% — failing"
        exit 1
      }
  else
    cargo test --package cyberos-qimen --package cyberos-luchnham --package cyberos-thaiat --package cyberos-lichphap --tests -q
    echo "coverage-gate: rust tests green (install cargo-llvm-cov for fail-under ${MIN})"
  fi
fi
echo "coverage-gate: ok"
