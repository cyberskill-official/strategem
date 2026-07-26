#!/usr/bin/env bash
# Full product journey against a live (or local) API + web.
# Defaults to production. No secrets committed — ephemeral user + PayOS mock seed.
#
# Usage:
#   bash scripts/smoke-prod-full.sh
#   API_BASE=http://127.0.0.1:18000 WEB_BASE=http://127.0.0.1:13000 bash scripts/smoke-prod-full.sh
#
# Env:
#   API_BASE          default https://api.strategem.cyberskill.world
#   WEB_BASE          default https://strategem-sepia.vercel.app
#   REQUIRE_RAG_LLM   default 1 — fail if interpretation is rule_based_degraded
#   SKIP_WEB          default 0 — set 1 to skip Vercel/page/BFF checks
set -euo pipefail

API_BASE="${API_BASE:-https://api.strategem.cyberskill.world}"
WEB_BASE="${WEB_BASE:-https://strategem-sepia.vercel.app}"
API_BASE="${API_BASE%/}"
WEB_BASE="${WEB_BASE%/}"
REQUIRE_RAG_LLM="${REQUIRE_RAG_LLM:-1}"
SKIP_WEB="${SKIP_WEB:-0}"

PASS=0
FAIL=0
WARN=0

pass() { PASS=$((PASS + 1)); printf '  [ok]   %s\n' "$*"; }
fail() { FAIL=$((FAIL + 1)); printf '  [FAIL] %s\n' "$*" >&2; }
warn() { WARN=$((WARN + 1)); printf '  [WARN] %s\n' "$*" >&2; }

json_get() {
  # json_get <json> <python-expr-on-d>
  local raw="$1"
  local expr="$2"
  printf '%s' "$raw" | python3 -c "import json,sys; d=json.load(sys.stdin); print($expr)"
}

http_json() {
  # http_json METHOD URL [DATA] — prints body; sets HTTP_CODE
  local method="$1" url="$2"
  local data="${3:-}"
  local tmp
  tmp="$(mktemp)"
  if [[ -n "$data" ]]; then
    HTTP_CODE="$(curl -sS -m 90 -o "$tmp" -w '%{http_code}' -X "$method" "$url" \
      -H 'content-type: application/json' \
      ${AUTH:+-H "$AUTH"} \
      -d "$data")" || HTTP_CODE="000"
  else
    HTTP_CODE="$(curl -sS -m 60 -o "$tmp" -w '%{http_code}' -X "$method" "$url" \
      ${AUTH:+-H "$AUTH"})" || HTTP_CODE="000"
  fi
  BODY="$(cat "$tmp")"
  rm -f "$tmp"
}

echo "== smoke-prod-full =="
echo "API_BASE=$API_BASE"
echo "WEB_BASE=$WEB_BASE"
echo

echo "== health =="
http_json GET "$API_BASE/healthz"
if [[ "$HTTP_CODE" == "200" ]] && printf '%s' "$BODY" | grep -q '"status"'; then
  pass "healthz"
else
  fail "healthz HTTP=$HTTP_CODE body=${BODY:0:120}"
fi

http_json GET "$API_BASE/ready"
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "ready"
  LLM_REACH="$(json_get "$BODY" "d.get('checks',{}).get('llm_reachable')")"
  LLM_DEG="$(json_get "$BODY" "d.get('degraded',{}).get('llm')")"
  echo "       llm_reachable=$LLM_REACH degraded.llm=$LLM_DEG"
else
  fail "ready HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

echo
echo "== auth + premium mock seed =="
TS="$(date +%s)"
EMAIL="smoke_prod_${TS}@example.com"
PASSWD='SmokePass123!'
AUTH=""

http_json POST "$API_BASE/auth/register" "{\"email\":\"$EMAIL\",\"password\":\"$PASSWD\"}"
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "register $EMAIL"
else
  fail "register HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

http_json POST "$API_BASE/auth/login" "{\"email\":\"$EMAIL\",\"password\":\"$PASSWD\"}"
if [[ "$HTTP_CODE" == "200" ]]; then
  TOKEN="$(json_get "$BODY" "d.get('access') or ''")"
  if [[ -n "$TOKEN" ]]; then
    AUTH="Authorization: Bearer $TOKEN"
    pass "login"
  else
    fail "login missing access token"
  fi
else
  fail "login HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

http_json GET "$API_BASE/auth/me"
USER_ID="$(json_get "$BODY" "d.get('user_id') or ''")"
TIER="$(json_get "$BODY" "d.get('tier') or ''")"
if [[ -n "$USER_ID" ]]; then
  pass "me user_id=$USER_ID tier=$TIER"
else
  fail "me HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

http_json POST "$API_BASE/api/v1/payments/checkout" \
  '{"plan_code":"premium","return_url":"'"$WEB_BASE"'/pricing"}'
# checkout body shape varies; accept 200 with provider/mode
if [[ "$HTTP_CODE" == "200" ]]; then
  MODE="$(json_get "$BODY" "d.get('mode') or (d.get('checkout_session') or {}).get('status') or 'ok'")"
  pass "checkout mode/status=$MODE"
else
  # retry minimal body used by some clients
  http_json POST "$API_BASE/api/v1/payments/checkout" '{"tier":"premium"}'
  if [[ "$HTTP_CODE" == "200" ]]; then
    pass "checkout (tier body)"
  else
    fail "checkout HTTP=$HTTP_CODE body=${BODY:0:200}"
  fi
fi

http_json POST "$API_BASE/api/v1/payments/mock-complete" \
  "{\"user_id\":\"$USER_ID\",\"tier\":\"premium\"}"
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "mock-complete premium"
else
  fail "mock-complete HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

http_json POST "$API_BASE/auth/login" "{\"email\":\"$EMAIL\",\"password\":\"$PASSWD\"}"
TOKEN="$(json_get "$BODY" "d.get('access') or ''")"
AUTH="Authorization: Bearer $TOKEN"
http_json GET "$API_BASE/auth/me"
TIER="$(json_get "$BODY" "d.get('tier') or ''")"
if [[ "$TIER" == "premium" ]]; then
  pass "tier=premium after re-login"
else
  fail "expected premium tier, got '$TIER'"
fi

echo
echo "== cast → report → pdf → follow-up → history =="
CAST_BODY='{"datetime":"2026-07-26T10:00:00+07:00","tz":"Asia/Ho_Chi_Minh","longitude":106.7,"question_type":"trach_thoi","persona_level":"learner"}'
http_json POST "$API_BASE/api/v1/calculate/qimen" "$CAST_BODY"
if [[ "$HTTP_CODE" != "200" ]]; then
  fail "cast qimen HTTP=$HTTP_CODE body=${BODY:0:300}"
  QID=""; RID=""
else
  QID="$(json_get "$BODY" "d.get('query_id') or ''")"
  RID="$(json_get "$BODY" "d.get('report_id') or ''")"
  PAT_N="$(json_get "$BODY" "len(d.get('patterns') or [])")"
  IMODE="$(json_get "$BODY" "(d.get('interpretation') or {}).get('mode') or ''")"
  MODEL="$(json_get "$BODY" "(d.get('ai_disclosure') or {}).get('model') or ''")"
  if [[ -n "$QID" && -n "$RID" && "$PAT_N" -gt 0 ]]; then
    pass "cast qid=$QID rid=$RID patterns=$PAT_N mode=$IMODE model=$MODEL"
  else
    fail "cast incomplete qid='$QID' rid='$RID' patterns=$PAT_N"
  fi
  if [[ "$REQUIRE_RAG_LLM" == "1" ]]; then
    if [[ "$IMODE" == "rule_based_degraded" ]]; then
      fail "interpretation degraded (REQUIRE_RAG_LLM=1) mode=$IMODE"
    else
      pass "interpretation not degraded (mode=$IMODE)"
    fi
  fi
fi

if [[ -n "${RID:-}" ]]; then
  http_json GET "$API_BASE/api/v1/reports/$RID"
  if [[ "$HTTP_CODE" == "200" ]]; then
    pass "report GET"
  else
    fail "report GET HTTP=$HTTP_CODE"
  fi
  PDF_TMP="$(mktemp)"
  PDF_CODE="$(curl -sS -m 60 -o "$PDF_TMP" -w '%{http_code}' \
    -H "$AUTH" "$API_BASE/api/v1/reports/$RID/pdf")" || PDF_CODE="000"
  if [[ "$PDF_CODE" == "200" ]] && head -c 4 "$PDF_TMP" | grep -q '%PDF'; then
    pass "pdf bytes=$(wc -c <"$PDF_TMP" | tr -d ' ')"
  else
    fail "pdf HTTP=$PDF_CODE magic=$(head -c 8 "$PDF_TMP" | xxd -p 2>/dev/null || true)"
  fi
  rm -f "$PDF_TMP"
fi

if [[ -n "${QID:-}" ]]; then
  http_json POST "$API_BASE/api/v1/queries/$QID/follow-up" \
    '{"message":"Cách cục nào đáng chú ý nhất và vì sao?","locale":"vi"}'
  if [[ "$HTTP_CODE" == "200" ]]; then
    ANS="$(json_get "$BODY" "(d.get('answer') or {}).get('beginner') or ''")"
    if [[ -n "$ANS" ]]; then
      pass "follow-up answer_len=${#ANS}"
    else
      fail "follow-up empty answer body=${BODY:0:200}"
    fi
  else
    fail "follow-up HTTP=$HTTP_CODE body=${BODY:0:200}"
  fi

  http_json GET "$API_BASE/api/v1/queries?limit=5"
  if [[ "$HTTP_CODE" == "200" ]]; then
    N="$(json_get "$BODY" "len(d.get('items') or (d if isinstance(d,list) else []))" )"
    if [[ "$N" -gt 0 ]]; then
      pass "history items=$N"
    else
      fail "history empty"
    fi
  else
    fail "history HTTP=$HTTP_CODE"
  fi
fi

echo
echo "== knowledge + edu =="
http_json GET "$API_BASE/api/v1/knowledge/patterns?limit=2"
if [[ "$HTTP_CODE" == "200" ]]; then
  TOTAL="$(json_get "$BODY" "d.get('total') or 0")"
  if [[ "$TOTAL" -ge 1 ]]; then
    pass "patterns total=$TOTAL"
  else
    fail "patterns total=$TOTAL"
  fi
else
  fail "patterns HTTP=$HTTP_CODE"
fi

http_json GET "$API_BASE/api/v1/knowledge/patterns?system=qimen&limit=1"
if [[ "$HTTP_CODE" == "200" ]]; then
  SYS="$(json_get "$BODY" "(d.get('patterns') or [{}])[0].get('system') if d.get('patterns') else ''")"
  pass "patterns filter system=${SYS:-unknown}"
else
  fail "patterns?system=qimen HTTP=$HTTP_CODE"
fi

http_json GET "$API_BASE/api/v1/knowledge/graph/nodes"
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "graph nodes"
else
  fail "graph nodes HTTP=$HTTP_CODE"
fi

http_json GET "$API_BASE/api/v1/edu/library?limit=3"
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "edu library"
else
  fail "edu library HTTP=$HTTP_CODE"
fi

http_json GET "$API_BASE/api/v1/edu/onboarding"
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "edu onboarding"
else
  fail "edu onboarding HTTP=$HTTP_CODE"
fi

http_json POST "$API_BASE/api/v1/edu/practice/grade" \
  '{"system":"qimen","answers":[{"item_id":"x","choice":"a"}]}'
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "edu practice grade"
else
  fail "edu practice HTTP=$HTTP_CODE body=${BODY:0:160}"
fi

http_json POST "$API_BASE/api/v1/calendar/convert" \
  '{"datetime":"2026-07-26T10:00:00+07:00","tz":"Asia/Ho_Chi_Minh"}'
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "calendar convert"
else
  fail "calendar HTTP=$HTTP_CODE"
fi

echo
echo "== timing / scenario / cross =="
http_json POST "$API_BASE/api/v1/timing/optimize" \
  '{"start":"2026-08-01T01:00:00Z","end":"2026-08-01T12:00:00Z","granularity":"gio","loai_cau_hoi":"trach_thoi","tz":"+07:00","longitude":106.7,"top_n":3}'
if [[ "$HTTP_CODE" == "200" ]]; then
  W="$(json_get "$BODY" "len(d.get('windows') or [])")"
  pass "timing windows=$W"
else
  fail "timing HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

http_json POST "$API_BASE/api/v1/scenario/compare" \
  '{"top_n":3,"scenarios":[{"label":"A","start":"2026-08-01T01:00:00Z","end":"2026-08-01T05:00:00Z","granularity":"gio"},{"label":"B","start":"2026-08-01T06:00:00Z","end":"2026-08-01T10:00:00Z","granularity":"gio"}]}'
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "scenario compare"
else
  fail "scenario HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

http_json POST "$API_BASE/api/v1/cross-system/validate" \
  '{"systems":["qimen","liuren"],"datetime":"2026-07-26T10:00:00+07:00","tz":"+07:00","longitude":106.7,"loai_cau_hoi":"trach_thoi"}'
if [[ "$HTTP_CODE" == "200" ]]; then
  pass "cross-system validate"
else
  fail "cross-system HTTP=$HTTP_CODE body=${BODY:0:200}"
fi

echo
echo "== CORS =="
CORS_HDR="$(curl -sS -m 15 -D- -o /dev/null -X OPTIONS "$API_BASE/api/v1/calculate/qimen" \
  -H "Origin: $WEB_BASE" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: authorization,content-type" \
  | tr -d '\r' | awk -F': ' 'tolower($1)=="access-control-allow-origin"{print $2; exit}')"
if [[ "$CORS_HDR" == "$WEB_BASE" ]]; then
  pass "CORS allow-origin=$CORS_HDR"
elif [[ "$WEB_BASE" == http://127.0.0.1:* || "$WEB_BASE" == http://localhost:* ]] && [[ -z "$CORS_HDR" ]]; then
  # Dev API may skip CORS middleware when CORS_ORIGINS unset — warn only locally.
  warn "CORS header absent on local API (dev middleware may be off)"
else
  fail "CORS expected $WEB_BASE got '${CORS_HDR:-none}'"
fi

if [[ "$SKIP_WEB" != "1" ]]; then
  echo
  echo "== web pages + BFF =="
  for p in / /login /signup /cast /patterns /library /learn /pricing /dashboard /help /timing /scenarios /cross-system /practice /manage/history /manage/settings; do
    CODE="$(curl -sS -m 30 -o /dev/null -w '%{http_code}' "$WEB_BASE$p" || echo 000)"
    if [[ "$CODE" == "200" ]]; then
      pass "web $p"
    else
      fail "web $p HTTP=$CODE"
    fi
  done

  WEB_EMAIL="web_${EMAIL}"
  http_json POST "$WEB_BASE/api/auth/signup" "{\"email\":\"$WEB_EMAIL\",\"password\":\"$PASSWD\"}"
  # http_json doesn't set AUTH for web; reuse BODY/HTTP_CODE
  if [[ "$HTTP_CODE" == "200" ]]; then
    pass "web BFF signup"
  else
    fail "web BFF signup HTTP=$HTTP_CODE body=${BODY:0:200}"
  fi

  # login via BFF without AUTH header
  tmp="$(mktemp)"
  HTTP_CODE="$(curl -sS -m 60 -o "$tmp" -w '%{http_code}' -X POST "$WEB_BASE/api/auth/login" \
    -H 'content-type: application/json' \
    -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWD\"}")" || HTTP_CODE="000"
  BODY="$(cat "$tmp")"; rm -f "$tmp"
  if [[ "$HTTP_CODE" == "200" ]] && printf '%s' "$BODY" | grep -q access; then
    pass "web BFF login"
  else
    fail "web BFF login HTTP=$HTTP_CODE body=${BODY:0:200}"
  fi
fi

echo
echo "== summary =="
echo "pass=$PASS warn=$WARN fail=$FAIL"
echo "smoke user=$EMAIL"
if [[ "$FAIL" -gt 0 ]]; then
  echo "smoke-prod-full: FAILED against $API_BASE" >&2
  exit 1
fi
echo "smoke-prod-full: OK against $API_BASE"
exit 0
