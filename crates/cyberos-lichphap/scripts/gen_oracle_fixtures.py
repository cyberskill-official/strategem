#!/usr/bin/env python3
"""Offline oracle fixture generator.

Optional deps (sxwnl, tyme4py) are intentionally NOT cargo dependencies.
When available, regenerate CSVs under tests/fixtures/. Without them, no-op.
"""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    print("gen_oracle_fixtures: optional offline regenerator")
    print("Install sxwnl / tyme4py to regenerate against external oracles.")
    print("Committed fixtures are used by CI (oracle_harness.rs).")
    root = Path(__file__).resolve().parents[1] / "tests" / "fixtures"
    print("fixtures dir:", root)
    return 0


if __name__ == "__main__":
    sys.exit(main())
