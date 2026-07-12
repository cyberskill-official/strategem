/**
 * Local pin store for saved charts — client-only, survives reloads.
 */

export type SavedChart = {
  query_id: string;
  he: string;
  question_type: string;
  cast_at: string;
  report_id?: string;
  pinned_at: string;
};

export const SAVED_CHARTS_KEY = "tamthuc.savedCharts.v1";

export function loadSavedCharts(): SavedChart[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(SAVED_CHARTS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as SavedChart[];
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

export function isPinned(queryId: string): boolean {
  return loadSavedCharts().some((c) => c.query_id === queryId);
}

export function pinChart(chart: Omit<SavedChart, "pinned_at">): SavedChart[] {
  const list = loadSavedCharts().filter((c) => c.query_id !== chart.query_id);
  const next: SavedChart[] = [
    { ...chart, pinned_at: new Date().toISOString() },
    ...list,
  ].slice(0, 48);
  localStorage.setItem(SAVED_CHARTS_KEY, JSON.stringify(next));
  return next;
}

export function unpinChart(queryId: string): SavedChart[] {
  const next = loadSavedCharts().filter((c) => c.query_id !== queryId);
  localStorage.setItem(SAVED_CHARTS_KEY, JSON.stringify(next));
  return next;
}

export function togglePin(chart: Omit<SavedChart, "pinned_at">): {
  pinned: boolean;
  list: SavedChart[];
} {
  if (isPinned(chart.query_id)) {
    return { pinned: false, list: unpinChart(chart.query_id) };
  }
  return { pinned: true, list: pinChart(chart) };
}
