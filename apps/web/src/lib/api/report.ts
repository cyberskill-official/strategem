/**
 * Report API client — FR-WEB-005 (reads FR-REPORT-001 StructuredReport).
 * Read-only: never mutates the report object.
 */

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

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api/v1";

/** Fetch a persisted StructuredReport by id (read-only). */
export async function getReport(reportId: string): Promise<StructuredReport> {
  const res = await fetch(`${API_BASE}/reports/${encodeURIComponent(reportId)}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) {
    throw new Error(`getReport failed: ${res.status}`);
  }
  return (await res.json()) as StructuredReport;
}

/** Trigger FR-REPORT-002 PDF export; client does not re-render the PDF. */
export async function downloadReportPdf(reportId: string): Promise<Blob> {
  const res = await fetch(
    `${API_BASE}/reports/${encodeURIComponent(reportId)}/pdf`,
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

/** Demo fixture used until the live report API is wired. */
export function demoReport(reportId: string): StructuredReport {
  return {
    report_id: reportId,
    query_id: "a0f1",
    chart_summary: {
      he: "ky_mon",
      dau_vao: {
        datetime: "2004-01-01T10:30:00",
        tz: "+07:00",
        kinh_do: 106.7,
        loai_cau_hoi: "trach_thoi",
      },
      lich_phap_summary:
        "Tu tru 癸未 甲子 戊午 丁巳 - tiet khi 冬至 (tam nguyen thuong)",
      key_positions: ["truc phu cung 1", "truc su 休門 cung 6"],
    },
    detected_patterns: [
      {
        id: "qimen_thanh_long_hoi_dau",
        name: "青龍返首",
        polarity: "cat",
        cung: 1,
        score: 0.9,
        citations: [{ source: "Yen Ba Dieu Tau Ca", locator: "cach cat" }],
      },
    ],
    interpretation: {
      beginner: "A cautious educational reading of the chart patterns.",
      expert: "Technical notes grounded in the retrieved classical units.",
      recommendations: ["Reflect on timing using the cited classical guidance."],
    },
    citations: [
      {
        source: "Yen Ba Dieu Tau Ca",
        locator: "cach cat",
        han: "青龍返首",
        bach_thoai: "Thanh long hồi đầu",
        dich: "Azure Dragon turns head — auspicious for major affairs.",
      },
    ],
    confidence: 0.72,
    ai_disclosure: {
      model: "stub-llm",
      limits: "decision support, not a verdict; no medical/legal/financial advice",
      review_status: "not_required",
    },
    created_at: "2026-07-08T12:00:05Z",
  };
}
