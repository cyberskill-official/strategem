"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ReportView } from "../../../src/components/report/report-view";
import {
  getReport,
  type StructuredReport,
} from "../../../src/lib/api/report";

/** Report view — live GET /api/v1/reports/{id}; no demo fixtures. */
export default function ReportPage() {
  const params = useParams();
  const reportId = String(params?.reportId ?? "");
  const [report, setReport] = useState<StructuredReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      if (!reportId) {
        setError("missing report id");
        setLoading(false);
        return;
      }
      try {
        const r = await getReport(reportId);
        if (!cancelled) setReport(r);
      } catch (e) {
        if (!cancelled)
          setError(e instanceof Error ? e.message : "Failed to load report");
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [reportId]);

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: 16 }}>
      {loading ? <p data-testid="report-loading">Loading…</p> : null}
      {error ? (
        <p data-testid="report-error" style={{ color: "var(--color-danger)" }}>
          {error}
        </p>
      ) : null}
      {report && !loading ? <ReportView report={report} /> : null}
    </div>
  );
}
