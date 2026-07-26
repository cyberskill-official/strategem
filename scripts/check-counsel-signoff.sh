#!/usr/bin/env bash
# LEGAL-004 release gate — fail closed while counsel sign-off is pending.
# Usage: bash scripts/check-counsel-signoff.sh
# Exit 0 only when gate-status.json verdict is approved (or approved-with-conditions
# with conditions_closed=true), and companion markers agree.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STATUS="$ROOT/docs/legal/vn-legal-review/gate-status.json"
RECORD="$ROOT/docs/legal/vn-legal-review/counsel-signoff-record.md"
COPY_KEYS="$ROOT/docs/legal/copy-deck/copy-keys.yaml"
TS_GATE="$ROOT/apps/web/src/lib/legal/counsel-gate.ts"

fail() {
  echo "LEGAL-004: $*" >&2
  exit 1
}

[[ -f "$STATUS" ]] || fail "missing gate-status.json — launch blocked"
[[ -f "$RECORD" ]] || fail "missing counsel-signoff-record.md — launch blocked"
[[ -f "$COPY_KEYS" ]] || fail "missing copy-keys.yaml — launch blocked"
[[ -f "$TS_GATE" ]] || fail "missing counsel-gate.ts — launch blocked"

# Parse JSON + markdown + yaml/ts mirrors via Python for consistent checks.
python3 - "$STATUS" "$RECORD" "$COPY_KEYS" "$TS_GATE" <<'PY'
import json
import re
import sys
from pathlib import Path

status_path, record_path, copy_keys_path, ts_path = map(Path, sys.argv[1:])

data = json.loads(status_path.read_text(encoding="utf-8"))
verdict = data.get("verdict")
counsel_review = data.get("counsel_review")
conditions_closed = data.get("conditions_closed", False)

allowed = {"pending", "approved", "approved-with-conditions", "rejected"}
if verdict not in allowed:
    print(f"LEGAL-004: invalid gate-status verdict={verdict!r}", file=sys.stderr)
    sys.exit(1)

record = record_path.read_text(encoding="utf-8")
# Table row: | Verdict | **pending** | or | Verdict | approved |
m = re.search(r"\|\s*Verdict\s*\|\s*\**([a-z-]+)\**\s*\|", record, re.I)
if not m:
    print("LEGAL-004: could not parse Verdict from counsel-signoff-record.md", file=sys.stderr)
    sys.exit(1)
record_verdict = m.group(1).lower()
if record_verdict != verdict:
    print(
        f"LEGAL-004: record Verdict={record_verdict!r} disagrees with "
        f"gate-status.json verdict={verdict!r}",
        file=sys.stderr,
    )
    sys.exit(1)

copy_keys = copy_keys_path.read_text(encoding="utf-8")
ck = re.search(r"counsel_review:\s*(\w+)", copy_keys)
if not ck:
    print("LEGAL-004: missing meta.counsel_review in copy-keys.yaml", file=sys.stderr)
    sys.exit(1)
copy_review = ck.group(1)
ts = ts_path.read_text(encoding="utf-8")
# Parse the COUNSEL_GATE_STATUS object only — type unions also contain
# counsel_review: "pending" | "approved" and must not win the match.
status_block = re.search(
    r"export const COUNSEL_GATE_STATUS[^=]*=\s*\{(.*?)\n\};",
    ts,
    re.S,
)
if not status_block:
    print("LEGAL-004: could not find COUNSEL_GATE_STATUS in counsel-gate.ts", file=sys.stderr)
    sys.exit(1)
block = status_block.group(1)
ts_verdict_m = re.search(r'verdict:\s*"([a-z-]+)"', block)
ts_review_m = re.search(r'counsel_review:\s*"([a-z-]+)"', block)
if not ts_verdict_m or not ts_review_m:
    print("LEGAL-004: could not parse COUNSEL_GATE_STATUS in counsel-gate.ts", file=sys.stderr)
    sys.exit(1)
ts_verdict = ts_verdict_m.group(1)
ts_review = ts_review_m.group(1)

if ts_verdict != verdict:
    print(
        f"LEGAL-004: counsel-gate.ts verdict={ts_verdict!r} disagrees with "
        f"gate-status.json verdict={verdict!r}",
        file=sys.stderr,
    )
    sys.exit(1)

# Launch-open path
if verdict in ("approved", "approved-with-conditions"):
    if verdict == "approved-with-conditions" and conditions_closed is not True:
        print(
            "LEGAL-004: approved-with-conditions but conditions_closed is not true — launch blocked",
            file=sys.stderr,
        )
        sys.exit(1)
    if counsel_review != "approved":
        print(
            f"LEGAL-004: verdict={verdict} but counsel_review={counsel_review!r} "
            "(expected approved)",
            file=sys.stderr,
        )
        sys.exit(1)
    if copy_review != "approved":
        print(
            f"LEGAL-004: copy-keys.yaml counsel_review={copy_review!r} "
            "(expected approved)",
            file=sys.stderr,
        )
        sys.exit(1)
    if ts_review != "approved":
        print(
            f"LEGAL-004: counsel-gate.ts counsel_review={ts_review!r} "
            "(expected approved)",
            file=sys.stderr,
        )
        sys.exit(1)
    print(
        f"LEGAL-004: counsel verdict={verdict} — gate open "
        "(confirm conditions closed if conditional)"
    )
    sys.exit(0)

print(
    f"LEGAL-004: counsel verdict={verdict} — public launch / app-store submission BLOCKED",
    file=sys.stderr,
)
print(
    f"Record a human counsel sign-off in {record_path} before release "
    "(see docs/legal/vn-legal-review/operator-runbook.md).",
    file=sys.stderr,
)
sys.exit(1)
PY
