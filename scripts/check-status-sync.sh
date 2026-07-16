#!/usr/bin/env bash
# Fail if docs/status board counts lag task frontmatter (CI + local).
# migrate-tasks --page regenerates the page; this only verifies freshness.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

specs=$(find docs/tasks -name 'spec.md' | wc -l | tr -d ' ')
done_n=$(grep -rh '^status:' docs/tasks --include='spec.md' | grep -c 'done' || true)
page="$root/docs/status/index.html"
[ -f "$page" ] || { echo "check-status-sync: missing $page — run: bash .cyberos/migrate-tasks.sh --page ."; exit 1; }

# Board embeds "done N" / "N tasks" style counters from the hub renderer
if ! grep -q "done ${done_n}\|${done_n} done\|${specs} tasks\|done / closed" "$page"; then
  echo "check-status-sync: docs/status/index.html does not reflect ${done_n}/${specs} done tasks"
  echo "  Run: bash .cyberos/migrate-tasks.sh --page . && git add docs/status"
  exit 1
fi

# Soft: ensure page mentions done count
if ! grep -qE "done ${done_n}|${done_n} done" "$page"; then
  echo "check-status-sync: WARN could not find exact done count ${done_n} in index.html (regen recommended)"
  # still fail hard so GitHub stays honest
  exit 1
fi

echo "check-status-sync: ok specs=${specs} done=${done_n}"
