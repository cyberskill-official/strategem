/**
 * Saved-chart history + share — TASK-WEB-007 (reads TASK-API-004, read-only).
 * Empty or failed fetches stay honest: never substitute unlabeled demo rows.
 */

import { apiBase } from "./client";
import { authHeaders } from "../auth/session";

export type ChartRef = {
  query_id: string;
  he: string;
  question_type: string;
  created_at: string;
  report_id?: string;
};

export type HistorySource = "live" | "empty" | "unauthorized" | "unavailable";

export async function getHistory(filter?: {
  he?: string;
  question_type?: string;
}): Promise<{ items: ChartRef[]; source: HistorySource }> {
  const base = apiBase();
  const q = new URLSearchParams();
  if (filter?.he) q.set("he", filter.he);
  if (filter?.question_type) q.set("question_type", filter.question_type);
  try {
    const res = await fetch(`${base}/api/v1/queries?${q}`, {
      method: "GET",
      headers: { Accept: "application/json", ...authHeaders() },
      cache: "no-store",
    });
    if (res.status === 401) return { items: [], source: "unauthorized" };
    if (!res.ok) return { items: [], source: "unavailable" };
    const body = (await res.json()) as { items?: ChartRef[] };
    const items = body.items ?? [];
    return { items, source: items.length ? "live" : "empty" };
  } catch {
    return { items: [], source: "unavailable" };
  }
}

export async function shareChart(queryId: string): Promise<{ url: string }> {
  return { url: `/results/${encodeURIComponent(queryId)}` };
}
