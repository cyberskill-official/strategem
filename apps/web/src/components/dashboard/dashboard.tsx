"use client";

import Link from "next/link";
import { FlowEntryCards } from "./flow-entry-cards";
import { QuickCast } from "./quick-cast";
import { RecentCharts, type ChartRef } from "./recent-charts";

const DEMO_RECENT: ChartRef[] = [
  {
    query_id: "demo-qimen-1",
    he: "ky_mon",
    question_type: "trach_thoi",
    cast_at: "2004-01-01T10:30:00",
  },
  {
    query_id: "demo-liuren-1",
    he: "luc_nham",
    question_type: "hon_nhan",
    cast_at: "2004-01-02T09:00:00",
  },
];

export function Dashboard() {
  return (
    <div data-testid="dashboard" style={{ maxWidth: 960, margin: "0 auto", display: "grid", gap: 24 }}>
      <h1>Dashboard</h1>
      <p data-testid="disclaimer" style={{ fontSize: 13, opacity: 0.8 }}>
        For cultural and educational use. Not medical, legal, or financial advice.
      </p>
      <QuickCast />
      <RecentCharts charts={DEMO_RECENT} title="Recent charts" />
      <RecentCharts charts={[]} title="Saved charts" emptyHint="Pin a chart from results to save it." />
      <FlowEntryCards />
      <p style={{ fontSize: 12 }}>
        <Link href="/cast">Go to full cast form</Link>
      </p>
    </div>
  );
}
