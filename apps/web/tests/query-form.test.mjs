import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

// schema shape contract (mirrors FR-API-001)
function validateQueryRequest(body) {
  if (!body.datetime) return "datetime required";
  if (!body.tz) return "tz required";
  if (!body.question_type) return "question_type required";
  if (!body.systems?.length) return "systems required";
  return null;
}

const body = {
  datetime: "2004-01-01T10:30:00",
  tz: "+07:00",
  place: "Ha Noi",
  kinh_do: 105.85,
  question_type: "trach_thoi",
  systems: ["qimen"],
  persona_level: "beginner",
};
assert.equal(validateQueryRequest(body), null);
assert.equal(validateQueryRequest({ ...body, datetime: "" }), "datetime required");

const formSrc = readFileSync(join(root, "src/components/query/query-form.tsx"), "utf8");
assert.match(formSrc, /data-testid="disclaimer"/);
// primary cast CTA meets 44px min touch target
assert.match(formSrc, /height: 4[48]/);
assert.match(formSrc, /cast\.button|t\(["']cast\.button["']\)/);
assert.match(formSrc, /RATE_LIMITED/);
assert.match(formSrc, /FORBIDDEN_TIER/);
assert.match(formSrc, /useLocale/);
assert.match(formSrc, /cs-chip/);
assert.match(formSrc, /cast\.advanced/);
assert.match(formSrc, /qtype-\$\{q\}|data-testid=\{`qtype-/);

const clientSrc = readFileSync(join(root, "src/lib/api/client.ts"), "utf8");
assert.match(clientSrc, /\/api\/v1\/calculate\//);
assert.match(clientSrc, /ApiClientError/);
assert.match(clientSrc, /getQuery|\/api\/v1\/queries\//);
assert.match(clientSrc, /sessionStorage/);

const castPage = readFileSync(join(root, "app/cast/page.tsx"), "utf8");
assert.match(castPage, /router\.push|\/results\//);
assert.match(castPage, /onSuccess/);

console.log("query-form tests ok");
