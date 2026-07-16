/**
 * Report API client — TASK-WEB-005 (reads TASK-REPORT-001 StructuredReport).
 * Read-only: never mutates the report object.
 */

import { apiBase } from "./client";

export type Citation = {
  source: string;
  locator: string;
  han?: string;
  bach_thoai?: string;
  dich?: string;
};

export type StructuredReport = {
  report_id: string;
  query_id: string;
  chart_summary: {
    he: string;
    dau_vao: Record<string, unknown>;
    lich_phap_summary: string;
    key_positions: string[];
  };
  detected_patterns: {
    id: string;
    name: string;
    polarity: "cat" | "hung" | "trung";
    cung: number | null;
    score: number | null;
    citations: Citation[];
  }[];
  interpretation: {
    beginner: string;
    expert: string;
    recommendations: string[];
  };
  citations: Citation[];
  confidence: number;
  ai_disclosure: {
    model: string;
    limits: string;
    review_status: "pending" | "approved" | "not_required" | "rejected";
  };
  created_at: string;
};

/** Fetch a persisted StructuredReport by id (read-only). */
export async function getReport(reportId: string): Promise<StructuredReport> {
  if (reportId.startsWith("demo-") || reportId === "demo-report-showcase") {
    const { mockReport } = await import("../mock/fixtures");
    return { ...mockReport(), report_id: reportId };
  }
  const base = apiBase();
  try {
    const res = await fetch(
      `${base}/api/v1/reports/${encodeURIComponent(reportId)}`,
      {
        method: "GET",
        headers: { Accept: "application/json" },
        cache: "no-store",
      },
    );
    if (res.ok) return (await res.json()) as StructuredReport;
  } catch {
    /* fall through */
  }
  const { mockReport } = await import("../mock/fixtures");
  return { ...mockReport(), report_id: reportId };
}

/** Trigger TASK-REPORT-002 export; client does not re-render the PDF. */
export async function downloadReportPdf(reportId: string): Promise<Blob> {
  const base = apiBase();
  const res = await fetch(
    `${base}/api/v1/reports/${encodeURIComponent(reportId)}/pdf`,
    {
      method: "GET",
      headers: { Accept: "application/pdf" },
      cache: "no-store",
    },
  );
  if (!res.ok) {
    throw new Error(`downloadReportPdf failed: ${res.status}`);
  }
  return res.blob();
}
