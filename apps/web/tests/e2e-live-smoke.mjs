/**
 * Live smoke (API + web static). Skips gracefully if servers down.
 * Run: node tests/e2e-live-smoke.mjs
 * Or with servers: API_BASE=http://127.0.0.1:8000 WEB_BASE=http://127.0.0.1:3000 node tests/e2e-live-smoke.mjs
 */
import assert from "node:assert/strict";

const API = (process.env.API_BASE || "http://127.0.0.1:8000").replace(/\/$/, "");
const WEB = (process.env.WEB_BASE || "http://127.0.0.1:3000").replace(/\/$/, "");

async function tryFetch(url, init) {
  try {
    const res = await fetch(url, { ...init, signal: AbortSignal.timeout(8000) });
    return res;
  } catch {
    return null;
  }
}

let skipped = 0;
let passed = 0;

const health = await tryFetch(`${API}/healthz`);
if (!health?.ok) {
  console.log("e2e-live-smoke: API down — skip live API checks");
  skipped++;
} else {
  const ready = await (await tryFetch(`${API}/ready`)).json();
  assert.equal(ready.status, "ok");
  console.log("ready", ready.checks?.engine_mode);
  for (const system of ["qimen", "liuren", "taiyi"]) {
    const res = await tryFetch(`${API}/api/v1/calculate/${system}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        datetime: "2004-01-01T10:30:00",
        tz: "+07:00",
        longitude: 105.85,
        place: "Ha Noi",
        question_type: "trach_thoi",
        systems: [system],
        persona_level: "beginner",
      }),
    });
    assert.ok(res?.ok, `${system} cast failed`);
    const body = await res.json();
    assert.ok(body.query_id);
    assert.ok(body.charts);
    if (system === "liuren") {
      const ban = Object.values(body.charts)[0]?.ban || {};
      const tdb = ban.thien_dia_ban || {};
      assert.equal((tdb.dia || []).length, 12, "LN dia length");
      assert.equal((tdb.thien || []).length, 12, "LN thien length");
    }
    passed++;
  }
  console.log("API casts ok");
}

const home = await tryFetch(WEB + "/");
if (!home?.ok) {
  console.log("e2e-live-smoke: WEB down — skip HTML checks");
  skipped++;
} else {
  const html = await home.text();
  assert.match(html, /Tam Thức|Strategem/);
  passed++;
  const cast = await tryFetch(WEB + "/cast");
  assert.ok(cast?.ok);
  passed++;
  console.log("WEB pages ok");
}

console.log(`e2e-live-smoke: passed=${passed} skipped_blocks=${skipped}`);
if (passed === 0) {
  console.log("e2e-live-smoke: no servers — treated as soft skip");
  process.exit(0);
}
console.log("e2e-live-smoke tests ok");
