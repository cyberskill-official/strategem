"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useLocale } from "../../../src/components/i18n/locale-provider";
import { ReportView } from "../../../src/components/report/report-view";
import {
  getReport,
  type StructuredReport,
} from "../../../src/lib/api/report";

export default function ReportPage() {
  const params = useParams();
  const reportId = String(params?.reportId ?? "");
  const { t } = useLocale();
  const [report, setReport] = useState<StructuredReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [demo, setDemo] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!reportId) {
        setError(t("report.error"));
        setLoading(false);
        return;
      }
      try {
        const r = await getReport(reportId);
        if (!cancelled) {
          setReport(r);
          setDemo(reportId.startsWith("demo-"));
        }
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : t("report.error"));
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [reportId, t]);

  return (
    <div className="cs-page cs-reveal">
      {demo ? (
        <div className="cs-banner cs-banner--ochre">{t("report.demoBanner")}</div>
      ) : null}
      {loading ? <p data-testid="report-loading">{t("report.loading")}</p> : null}
      {error ? (
        <p data-testid="report-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      ) : null}
      {report && !loading ? <ReportView report={report} /> : null}
    </div>
  );
}
