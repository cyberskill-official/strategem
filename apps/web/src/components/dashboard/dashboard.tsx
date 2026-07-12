"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getHistory, type ChartRef } from "../../lib/api/history";
import { loadSavedCharts, type SavedChart } from "../../lib/pins/saved-charts";
import { useLocale } from "../i18n/locale-provider";
import { FlowEntryCards } from "./flow-entry-cards";
import { QuickCast } from "./quick-cast";
import { RecentCharts } from "./recent-charts";

export function Dashboard() {
  const { t } = useLocale();
  const [recent, setRecent] = useState<ChartRef[]>([]);
  const [saved, setSaved] = useState<SavedChart[]>([]);
  const [source, setSource] = useState<"live" | "demo" | "loading">("loading");

  useEffect(() => {
    let cancelled = false;
    setSaved(loadSavedCharts());
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
    const onFocus = () => setSaved(loadSavedCharts());
    window.addEventListener("focus", onFocus);
    return () => {
      cancelled = true;
      window.removeEventListener("focus", onFocus);
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

      <div
        className="cs-card"
        style={{ display: "flex", flexWrap: "wrap", gap: 16, alignItems: "center" }}
      >
        <QuickCast />
        <span className="cs-muted">
          {source === "live"
            ? t("dashboard.liveFromApi")
            : source === "demo"
              ? t("dashboard.demoHint")
              : "…"}
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

      <div className="cs-card" data-testid="saved-charts-section">
        <RecentCharts
          charts={saved.map((c) => ({
            query_id: c.query_id,
            he: c.he,
            question_type: c.question_type,
            cast_at: c.cast_at,
          }))}
          title={t("dashboard.saved")}
          emptyHint={t("dashboard.savedEmpty")}
        />
      </div>

      <FlowEntryCards />

      <p className="cs-muted">
        <Link href="/cast">{t("dashboard.fullForm")}</Link>
        {" · "}
        <Link href="/learn">{t("nav.learn")}</Link>
      </p>
    </div>
  );
}
