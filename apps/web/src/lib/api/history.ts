/**
 * Saved-chart history + share — FR-WEB-007 (reads FR-API-004, read-only).
 */

export type ChartRef = {
  query_id: string;
  he: string;
  question_type: string;
  created_at: string;
  report_id?: string;
};

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api/v1";

export async function getHistory(filter?: {
  he?: string;
  question_type?: string;
}): Promise<ChartRef[]> {
  const q = new URLSearchParams();
  if (filter?.he) q.set("he", filter.he);
  if (filter?.question_type) q.set("question_type", filter.question_type);
  const res = await fetch(`${API_BASE}/history?${q}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`getHistory failed: ${res.status}`);
  const body = (await res.json()) as { items?: ChartRef[] };
  return body.items ?? [];
}

export async function shareChart(
  queryId: string,
): Promise<{ url: string }> {
  return { url: `/results/${encodeURIComponent(queryId)}` };
}

export function demoHistory(): ChartRef[] {
  return [
    {
      query_id: "q1",
      he: "ky_mon",
      question_type: "trach_thoi",
      created_at: "2026-07-08T12:00:00Z",
      report_id: "r1",
    },
    {
      query_id: "q2",
      he: "luc_nham",
      question_type: "chu_khach",
      created_at: "2026-07-07T09:00:00Z",
    },
  ];
}
