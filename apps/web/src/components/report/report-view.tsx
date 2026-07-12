"use client";

import type { StructuredReport } from "../../lib/api/report";
import { ChartSummarySection } from "./chart-summary-section";
import { InterpretationSection } from "./interpretation-section";
import { PdfDownloadButton } from "./pdf-download-button";

/**
 * Report view — FR-WEB-005.
 * Deterministic region visually separated from AI region.
 * Report object is read-only; this component never mutates it.
 */
export function ReportView({
  report,
  downloadFn,
}: {
  report: StructuredReport;
  downloadFn?: (id: string) => Promise<Blob>;
}) {
  // Read-only snapshot reference — do not mutate
  const snapshot = report;

  return (
    <div data-testid="report-view" style={{ display: "grid", gap: 24 }}>
      <header>
        <h1 style={{ fontSize: "var(--text-xl)", marginBottom: 4 }}>
          Report · {snapshot.report_id}
        </h1>
        <p style={{ opacity: 0.7, margin: 0 }}>
          Query {snapshot.query_id} · {snapshot.created_at}
        </p>
      </header>

      <ChartSummarySection report={snapshot} />

      <hr
        data-testid="region-boundary"
        style={{ border: "none", borderTop: "2px dashed var(--color-border)" }}
        aria-hidden
      />

      <InterpretationSection report={snapshot} />

      <PdfDownloadButton
        reportId={snapshot.report_id}
        downloadFn={downloadFn}
      />
    </div>
  );
}
