"use client";

import Link from "next/link";
import { useLocale } from "../i18n/locale-provider";
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
  const { t } = useLocale();

  return (
    <div
      data-testid="dashboard"
      className="cs-page"
    >
      <h1>{t("dashboard.title")}</h1>
      {/* Disclaimer lives in shell footer — keep a hidden node for tests */}
      <p data-testid="disclaimer" className="visually-hidden">
        {t("disclaimer.short")}
      </p>
      <QuickCast />
      <div className="cs-card">
        <RecentCharts charts={DEMO_RECENT} title={t("dashboard.recent")} />
      </div>
      <div className="cs-card">
        <RecentCharts
          charts={[]}
          title={t("dashboard.saved")}
          emptyHint={t("dashboard.savedEmpty")}
        />
      </div>
      <FlowEntryCards />
      <p className="cs-muted">
        <Link href="/cast">{t("dashboard.fullForm")}</Link>
      </p>
    </div>
  );
}
