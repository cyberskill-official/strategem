"use client";

import { useState } from "react";
import { downloadReportPdf } from "../../lib/api/report";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

/**
 * PDF download triggers FR-REPORT-002 export by report_id.
 * Client does not re-render the PDF itself.
 */
export function PdfDownloadButton({
  reportId,
  downloadFn = downloadReportPdf,
}: {
  reportId: string;
  downloadFn?: (id: string) => Promise<Blob>;
}) {
  const { t } = useLocale();
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const onClick = async () => {
    setBusy(true);
    setErr(null);
    try {
      const blob = await downloadFn(reportId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `report-${reportId}.pdf`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (e) {
      setErr(e instanceof Error ? e.message : t("error.generic"));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div data-testid="pdf-download">
      <Button
        type="button"
        data-testid="pdf-download-button"
        onClick={onClick}
        disabled={busy}
        variant="secondary"
      >
        {busy ? t("report.pdfBusy") : t("report.pdf")}
      </Button>
      {err ? (
        <p data-testid="pdf-error" role="alert">
          {err}
        </p>
      ) : null}
    </div>
  );
}
