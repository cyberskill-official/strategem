/**
 * Saved-chart history + share — FR-WEB-007 (reads FR-API-004, read-only).
 */

import { apiBase } from "./client";

export type ChartRef = {
  query_id: string;
  he: string;
  question_type: string;
  created_at: string;
  report_id?: string;
};

export async function getHistory(filter?: {
  he?: string;
  question_type?: string;
}): Promise<ChartRef[]> {
  const base = apiBase();
  const q = new URLSearchParams();
  if (filter?.he) q.set("he", filter.he);
  if (filter?.question_type) q.set("question_type", filter.question_type);
  const res = await fetch(`${base}/api/v1/queries?${q}`, {
    method: "GET",
    headers: { Accept: "application/json" },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(`getHistory failed: ${res.status}`);
  const body = (await res.json()) as { items?: ChartRef[] };
  return body.items ?? [];
}

export async function shareChart(queryId: string): Promise<{ url: string }> {
  return { url: `/results/${encodeURIComponent(queryId)}` };
}
