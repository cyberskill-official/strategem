"use client";

import { useLocale } from "../i18n/locale-provider";

/**
 * Export triggers TASK-REPORT-002 PDF and TASK-CHART-004 PNG/SVG —
 * client does not re-render the files.
 */
export function ExportMenu({
  queryId,
  reportId,
  onPdf,
  onPng,
  onSvg,
}: {
  queryId: string;
  reportId?: string;
  onPdf?: (reportId: string) => void;
  onPng?: (queryId: string) => void;
  onSvg?: (queryId: string) => void;
}) {
  const { t } = useLocale();
  return (
    <div data-testid="export-menu" style={{ display: "inline-flex", gap: 4 }}>
      <button
        type="button"
        data-testid="export-pdf"
        disabled={!reportId}
        onClick={() => reportId && onPdf?.(reportId)}
      >
        {t("export.pdf")}
      </button>
      <button
        type="button"
        data-testid="export-png"
        onClick={() => onPng?.(queryId)}
      >
        {t("export.png")}
      </button>
      <button
        type="button"
        data-testid="export-svg"
        onClick={() => onSvg?.(queryId)}
      >
        {t("export.svg")}
      </button>
    </div>
  );
}
