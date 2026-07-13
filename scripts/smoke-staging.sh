#!/usr/bin/env bash
# COV-020: smoke KM/LN/TA against a staging or local API base URL.
# Secrets never required for cast path. Usage:
#   API_BASE=https://api.staging.example.com bash scripts/smoke-staging.sh
#   API_BASE=http://127.0.0.1:18000 bash scripts/smoke-staging.sh
set -euo pipefail
API_BASE="${API_BASE:-http://127.0.0.1:8000}"
API_BASE="${API_BASE%/}"

echo "== healthz =="
curl -sS -m 10 "$API_BASE/healthz" | tee /dev/stderr | grep -q '"status":"ok\|"status": "ok"'
echo
echo "== ready =="
curl -sS -m 10 "$API_BASE/ready" | tee /dev/stderr
echo

payload='{"datetime":"2004-01-01T10:30:00","tz":"+07:00","longitude":106.7,"systems":["SYS"],"question_type":"trach_thoi","persona_level":"beginner"}'
for sys in qimen liuren taiyi; do
  echo "== cast $sys =="
  body="${payload//SYS/$sys}"
  out=$(curl -sS -m 30 -X POST "$API_BASE/api/v1/calculate/$sys" \
    -H 'content-type: application/json' \
    -d "$body")
  echo "$out" | python3 -c "
import sys,json
d=json.load(sys.stdin)
assert d.get('charts'), d
ch=list(d['charts'].values())[0]
assert ch.get('he') or ch.get('ban'), ch
print('ok', ch.get('he'), 'ban_keys', list((ch.get('ban') or {}).keys())[:6])
"
done
echo "smoke-staging: all systems ok against $API_BASE"
