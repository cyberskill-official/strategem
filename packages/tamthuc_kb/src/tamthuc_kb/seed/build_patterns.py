"""CLI entry: validate seed and print counts — FR-KB-002."""

from __future__ import annotations

from tamthuc_kb.seed.loader import load_all_patterns


def main() -> int:
    rows = load_all_patterns()
    by = {"qimen": 0, "liuren": 0, "taiyi": 0}
    for r in rows:
        by[r["system"]] += 1
    print(f"patterns total={len(rows)} {by}")
    assert 150 <= len(rows) <= 200, "coverage target 150-200"
    assert by["qimen"] >= 90
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
