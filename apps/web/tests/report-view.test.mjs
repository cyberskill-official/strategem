import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const reportView = readFileSync(
  join(root, "src/components/report/report-view.tsx"),
  "utf8",
);
const chartSummary = readFileSync(
  join(root, "src/components/report/chart-summary-section.tsx"),
  "utf8",
);
const interp = readFileSync(
  join(root, "src/components/report/interpretation-section.tsx"),
  "utf8",
);
const cites = readFileSync(
  join(root, "src/components/report/citation-list.tsx"),
  "utf8",
);
const pdf = readFileSync(
  join(root, "src/components/report/pdf-download-button.tsx"),
  "utf8",
);
const api = readFileSync(join(root, "src/lib/api/report.ts"), "utf8");
const page = readFileSync(
  join(root, "app/report/[reportId]/page.tsx"),
  "utf8",
);

assert.match(reportView, /deterministic-region|ChartSummarySection/);
assert.match(reportView, /InterpretationSection/);
assert.match(reportView, /region-boundary/);
assert.match(reportView, /PdfDownloadButton/);
assert.doesNotMatch(reportView, /report\.\w+\s*=/);

assert.match(chartSummary, /deterministic-region/);
assert.match(chartSummary, /polarity-badge/);
assert.match(chartSummary, /icon|polarity\.(cat|hung|trung)/);
assert.match(chartSummary, /polarity\.label|Polarity/);

assert.match(interp, /AIDisclosureBadge/);
assert.match(interp, /PersonaToggle/);
assert.match(interp, /not-yet-approved|pending/);
assert.match(interp, /confidence-supporting/);

assert.match(cites, /cite-han/);
assert.match(cites, /cite-bach/);
assert.match(cites, /cite-dich/);
assert.match(cites, /cite-locator/);

assert.match(pdf, /downloadReportPdf|downloadFn/);
assert.match(pdf, /pdf-download-button/);

assert.match(api, /getReport/);
assert.match(api, /downloadReportPdf/);
assert.match(api, /StructuredReport/);
assert.doesNotMatch(api, /demoReport/);

assert.match(page, /ReportView|getReport/);
assert.match(page, /reportId|getReport/);
assert.doesNotMatch(page, /demoReport/);

console.log("report-view tests ok");
