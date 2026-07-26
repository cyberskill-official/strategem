#!/usr/bin/env bash
# Fail if docs/status board counts lag task frontmatter (CI + local).
# migrate-tasks --page regenerates the page; this only verifies freshness.
# Also rewrites post-migrate status.html → index.html under docs/status/ so
# hub@3 landing stays green without editing the gitignored .cyberos renderer.
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
cd "$root"

status_dir="$root/docs/status"
page="$status_dir/index.html"

# Post-migrate: migrate copies reference/status.html → docs/status/index.html but
# generated sibling pages still link to status.html. Rewrite to index.html.
if [ -d "$status_dir" ]; then
  while IFS= read -r -d '' f; do
    if grep -q 'status\.html' "$f" 2>/dev/null; then
      # macOS/BSD and GNU sed both accept -i.bak then remove backup
      sed -i.bak \
        -e 's|href="status\.html|href="index.html|g' \
        -e 's|url=status\.html|url=index.html|g' \
        -e "s|href='status\\.html|href='index.html|g" \
        "$f"
      rm -f "${f}.bak"
    fi
  done < <(find "$status_dir" -maxdepth 1 -type f \( -name '*.html' -o -name '*.htm' \) -print0)
fi

specs=$(find docs/tasks -name 'spec.md' | wc -l | tr -d ' ')
done_n=$(grep -rh '^status:' docs/tasks --include='spec.md' | grep -c 'done' || true)
[ -f "$page" ] || { echo "check-status-sync: missing $page — run: bash .cyberos/migrate-tasks.sh --page ."; exit 1; }

feed_ok=0
if grep -q 'id="sv3-data"' "$page"; then
  # hub@3: prefer #sv3-data JSON — tasks.length vs specs, s==="done" vs frontmatter done
  if ! command -v python3 >/dev/null 2>&1; then
    echo "check-status-sync: python3 required to validate hub@3 #sv3-data"
    exit 1
  fi
  parsed="$(python3 -c "
import json, re, sys
html = open(sys.argv[1], encoding='utf-8').read()
m = re.search(r'id=\"sv3-data\">(.*?)</script>', html, re.S)
if not m:
    print('MISSING')
    raise SystemExit(0)
try:
    data = json.loads(m.group(1))
except json.JSONDecodeError:
    print('BAD_JSON')
    raise SystemExit(0)
tasks = data.get('tasks') or []
done = sum(1 for t in tasks if t.get('s') == 'done')
print('%d %d' % (len(tasks), done))
" "$page")"
  if [ -z "$parsed" ] || [ "$parsed" = "MISSING" ] || [ "$parsed" = "BAD_JSON" ]; then
    echo "check-status-sync: hub@3 #sv3-data present but unreadable ($parsed)"
    echo "  Run: bash .cyberos/migrate-tasks.sh --page . && git add docs/status"
    exit 1
  fi
  feed_specs="${parsed%% *}"
  feed_done="${parsed##* }"
  if [ "$feed_specs" = "$specs" ] && [ "$feed_done" = "$done_n" ]; then
    feed_ok=1
  else
    echo "check-status-sync: #sv3-data counts mismatch (feed=${feed_done}/${feed_specs} disk=${done_n}/${specs})"
    echo "  Run: bash .cyberos/migrate-tasks.sh --page . && git add docs/status"
    exit 1
  fi
fi

if [ "$feed_ok" != "1" ]; then
  # Legacy / greppable fallback: "done N" / "N done" / "N tasks" / "done / closed"
  if ! grep -qE "done ${done_n}|${done_n} done|${specs} tasks|done / closed" "$page"; then
    echo "check-status-sync: docs/status/index.html does not reflect ${done_n}/${specs} done tasks"
    echo "  Run: bash .cyberos/migrate-tasks.sh --page . && git add docs/status"
    exit 1
  fi
  if ! grep -qE "done ${done_n}|${done_n} done" "$page"; then
    echo "check-status-sync: WARN could not find exact done count ${done_n} in index.html (regen recommended)"
    exit 1
  fi
fi

echo "check-status-sync: ok specs=${specs} done=${done_n}"
