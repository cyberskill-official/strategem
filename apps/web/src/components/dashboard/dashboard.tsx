"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getHistory, type ChartRef } from "../../lib/api/history";
import { useLocale } from "../i18n/locale-provider";
import { FlowEntryCards } from "./flow-entry-cards";
import { QuickCast } from "./quick-cast";
import { RecentCharts } from "./recent-charts";

export function Dashboard() {
  const { t } = useLocale();
  const [recent, setRecent] = useState<ChartRef[]>([]);
  const [source, setSource] = useState<"live" | "demo" | "loading">("loading");

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const res = await getHistory();
        if (cancelled) return;
        setRecent(res.items.slice(0, 6));
        setSource(res.source);
      } catch {
        if (!cancelled) {
          setRecent([]);
          setSource("demo");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <div data-testid="dashboard" className="cs-page cs-reveal">
      <header>
        <p className="cs-kicker">{t("app.tagline")}</p>
        <h1>{t("dashboard.title")}</h1>
        <p className="cs-muted" style={{ maxWidth: "52ch" }}>
          {t("dashboard.lead")}
        </p>
      </header>
      <p data-testid="disclaimer" className="visually-hidden">
        {t("disclaimer.short")}
      </p>

      <div className="cs-card" style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "center" }}>
        <QuickCast />
        <span className="cs-muted">
          {source === "live" ? t("dashboard.liveFromApi") : source === "demo" ? t("dashboard.demoHint") : "…"}
        </span>
      </div>

      <div className="cs-card">
        <RecentCharts
          charts={recent.map((c) => ({
            query_id: c.query_id,
            he: c.he,
            question_type: c.question_type,
            cast_at: c.created_at,
          }))}
          title={t("dashboard.recent")}
        />
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
