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
}): Promise<{ items: ChartRef[]; source: "live" | "demo" }> {
  const base = apiBase();
  const q = new URLSearchParams();
  if (filter?.he) q.set("he", filter.he);
  if (filter?.question_type) q.set("question_type", filter.question_type);
  try {
    const res = await fetch(`${base}/api/v1/queries?${q}`, {
      method: "GET",
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (res.ok) {
      const body = (await res.json()) as { items?: ChartRef[] };
      const items = body.items ?? [];
      if (items.length) return { items, source: "live" };
    }
  } catch {
    /* fall through to demo */
  }
  const { mockHistory } = await import("../mock/fixtures");
  let items = mockHistory();
  if (filter?.he) items = items.filter((i) => i.he === filter.he);
  if (filter?.question_type)
    items = items.filter((i) => i.question_type === filter.question_type);
  return { items, source: "demo" };
}

export async function shareChart(queryId: string): Promise<{ url: string }> {
  return { url: `/results/${encodeURIComponent(queryId)}` };
}
