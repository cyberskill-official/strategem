/**
 * COV-009: login/signup pages + httpOnly cookie route handlers + live proxy path.
 *
 * Static source asserts always run. When WEB_BASE is set (or default local web is
 * reachable), also POST /api/auth/signup|login against the shipped Next routes —
 * fails hard on ECONNREFUSED / 500 from misconfigured API_URL (Docker bug).
 */
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const login = readFileSync(join(root, "app/login/page.tsx"), "utf8");
const signup = readFileSync(join(root, "app/signup/page.tsx"), "utf8");
const loginRoute = readFileSync(join(root, "app/api/auth/login/route.ts"), "utf8");
const signupRoute = readFileSync(join(root, "app/api/auth/signup/route.ts"), "utf8");
const compose = readFileSync(
  join(root, "../../deploy/compose/docker-compose.local.yml"),
  "utf8",
);
const webDockerfile = readFileSync(join(root, "../../deploy/docker/web.Dockerfile"), "utf8");
const vi = JSON.parse(readFileSync(join(root, "src/messages/vi.json"), "utf8"));

assert.match(login, /data-testid="login-page"/);
assert.match(signup, /data-testid="signup-page"/);
assert.match(loginRoute, /httpOnly:\s*true/);
assert.match(loginRoute, /tamthuc_refresh/);
assert.match(signupRoute, /httpOnly:\s*true/);
// Server must not fall back to NEXT_PUBLIC_API_BASE (host URL inside Docker).
assert.match(loginRoute, /serverApiBase|API_URL/);
assert.doesNotMatch(
  loginRoute.replace(/\/\*\*[\s\S]*?\*\//g, "").replace(/\/\/.*/g, ""),
  /NEXT_PUBLIC_API_BASE/,
);
assert.doesNotMatch(
  signupRoute.replace(/\/\*\*[\s\S]*?\*\//g, "").replace(/\/\/.*/g, ""),
  /NEXT_PUBLIC_API_BASE/,
);
assert.match(compose, /API_URL:\s*\$\{API_URL:-http:\/\/api:8000\}/);
assert.match(webDockerfile, /API_URL=http:\/\/api:8000|ENV API_URL=http:\/\/api:8000/);
assert.equal(typeof vi["auth.loginTitle"], "string");
assert.equal(typeof vi["nav.login"], "string");

const WEB_BASE = (process.env.WEB_BASE || "http://127.0.0.1:13000").replace(/\/$/, "");
const email = `cov009_${Date.now()}@example.com`;
const password = "password123";

async function probeWeb(base) {
  try {
    const r = await fetch(`${base}/login`, { signal: AbortSignal.timeout(3000) });
    return r.ok || r.status === 200;
  } catch {
    return false;
  }
}

const live = await probeWeb(WEB_BASE);
if (!live) {
  console.log(
    `auth-pages-cov009.test.mjs ok (static only; web not reachable at ${WEB_BASE})`,
  );
  process.exit(0);
}

// Live: signup through Next route → must not 500 on ECONNREFUSED
const signupRes = await fetch(`${WEB_BASE}/api/auth/signup`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password }),
  signal: AbortSignal.timeout(15000),
});
const signupBody = await signupRes.json().catch(() => ({}));
assert.notEqual(
  signupRes.status,
  500,
  `signup returned 500 (likely API_URL wrong inside web container): ${JSON.stringify(signupBody)}`,
);
assert.ok(
  signupRes.status === 200 || signupRes.status === 400 || signupRes.status === 409 || signupRes.status === 422,
  `unexpected signup status ${signupRes.status}: ${JSON.stringify(signupBody)}`,
);
if (signupRes.status === 200) {
  assert.ok(signupBody.access, `signup 200 missing access: ${JSON.stringify(signupBody)}`);
  const setCookie = signupRes.headers.getSetCookie?.() || [];
  const cookieJoined = setCookie.join(";") + (signupRes.headers.get("set-cookie") || "");
  assert.match(cookieJoined, /tamthuc_refresh/, "signup must set httpOnly refresh cookie");
}

// Live: login through Next route
const loginRes = await fetch(`${WEB_BASE}/api/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email, password }),
  signal: AbortSignal.timeout(15000),
});
const loginBody = await loginRes.json().catch(() => ({}));
assert.notEqual(
  loginRes.status,
  500,
  `login returned 500 (API_URL misconfigured): ${JSON.stringify(loginBody)}`,
);
if (signupRes.status === 200) {
  assert.equal(loginRes.status, 200, `login after signup: ${JSON.stringify(loginBody)}`);
  assert.ok(loginBody.access, "login missing access token");
}

console.log(
  `auth-pages-cov009.test.mjs ok (static + live ${WEB_BASE} signup=${signupRes.status} login=${loginRes.status})`,
);
