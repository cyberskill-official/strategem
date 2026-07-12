"use client";

import type { StructuredReport } from "../../lib/api/report";
import { useLocale } from "../i18n/locale-provider";
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
  const { t } = useLocale();
  const snapshot = report;

  return (
    <div data-testid="report-view" style={{ display: "grid", gap: 24 }}>
      <header>
        <h1 style={{ marginBottom: 4 }}>
          {t("report.title")} · {snapshot.report_id}
        </h1>
        <p className="cs-muted" style={{ margin: 0 }}>
          {t("report.query")} {snapshot.query_id} · {snapshot.created_at}
        </p>
      </header>

      <ChartSummarySection report={snapshot} />

      <hr
        data-testid="region-boundary"
        className="cs-region-boundary"
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
