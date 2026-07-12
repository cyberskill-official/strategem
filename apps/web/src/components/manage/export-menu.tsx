"use client";

/**
 * Export triggers FR-REPORT-002 PDF and FR-CHART-004 PNG/SVG —
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
  return (
    <div data-testid="export-menu" style={{ display: "inline-flex", gap: 4 }}>
      <button
        type="button"
        data-testid="export-pdf"
        disabled={!reportId}
        onClick={() => reportId && onPdf?.(reportId)}
      >
        PDF
      </button>
      <button
        type="button"
        data-testid="export-png"
        onClick={() => onPng?.(queryId)}
      >
        PNG
      </button>
      <button
        type="button"
        data-testid="export-svg"
        onClick={() => onSvg?.(queryId)}
      >
        SVG
      </button>
    </div>
  );
}
