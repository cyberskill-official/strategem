import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const read = (p) => readFileSync(join(root, p), "utf8");

const history = read("src/components/manage/history-list.tsx");
const flags = read("src/components/manage/school-flags-form.tsx");
const school = read("src/lib/flags/school-flags.ts");
const histApi = read("src/lib/api/history.ts");
const share = read("src/components/manage/share-dialog.tsx");
const exp = read("src/components/manage/export-menu.tsx");
const histPage = read("app/manage/history/page.tsx");
const setPage = read("app/manage/settings/page.tsx");

assert.match(history, /history-list/);
assert.match(history, /filter-he/);
assert.match(history, /\/results\//);
assert.match(history, /\/report\//);
assert.match(history, /ShareDialog|shareChart/);
assert.match(history, /useLocale/);

assert.match(flags, /school-flags-form/);
assert.match(flags, /fairness-note|settings\.fairness/);
assert.match(flags, /toCastOverrides/);
assert.match(flags, /dingju_method|default/);

assert.match(school, /dingju_method/);
assert.match(school, /pan_method/);
assert.match(school, /yin_yang_pan/);
assert.match(school, /khoi_quy_nhan/);
assert.match(school, /epoch/);
assert.match(school, /use_true_solar_time/);
assert.match(school, /toCastOverrides/);
assert.doesNotMatch(school, /correct school/i);

assert.match(histApi, /getHistory/);
assert.match(histApi, /shareChart/);
assert.match(histApi, /ChartRef/);
assert.match(histApi, /\/api\/v1\/queries/);
assert.doesNotMatch(histApi, /demoHistory/);
assert.doesNotMatch(histApi, /mockHistory/);

assert.match(share, /share-dialog/);
assert.match(exp, /export-pdf/);
assert.match(exp, /export-png/);
assert.match(exp, /export-svg/);

assert.match(histPage, /HistoryList|getHistory/);
assert.doesNotMatch(histPage, /demoHistory/);
assert.doesNotMatch(histPage, /history-demo-banner/);
assert.match(setPage, /SchoolFlagsForm/);

assert.match(school, /loadSchoolConfig|SCHOOL_FLAGS_STORAGE_KEY/);
assert.match(school, /toCastPayloadFlags/);

const form = read("src/components/query/query-form.tsx");
assert.match(form, /loadSchoolConfig|toCastPayloadFlags/);
assert.match(form, /co_truong_phai/);

console.log("management-flow tests ok");
