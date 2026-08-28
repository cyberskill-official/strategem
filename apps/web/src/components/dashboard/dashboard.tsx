"use client";

import Link from "next/link";
import { useEffect, useState, useSyncExternalStore } from "react";
import { getHistory, type ChartRef, type HistorySource } from "../../lib/api/history";
import { loadSavedCharts, type SavedChart } from "../../lib/pins/saved-charts";
import { useLocale } from "../i18n/locale-provider";
import { FlowEntryCards } from "./flow-entry-cards";
import { QuickCast } from "./quick-cast";
import { RecentCharts } from "./recent-charts";

const PIN_EVENT = "tamthuc:pins-changed";

function subscribePins(onChange: () => void) {
  if (typeof window === "undefined") return () => {};
  const handler = () => onChange();
  window.addEventListener(PIN_EVENT, handler);
  window.addEventListener("storage", handler);
  window.addEventListener("focus", handler);
  return () => {
    window.removeEventListener(PIN_EVENT, handler);
    window.removeEventListener("storage", handler);
    window.removeEventListener("focus", handler);
  };
}

function useSavedCharts(): SavedChart[] {
  return useSyncExternalStore(subscribePins, loadSavedCharts, () => []);
}

function historyStatusKey(source: HistorySource | "loading"): string | null {
  switch (source) {
    case "live":
      return "dashboard.liveFromApi";
    case "unauthorized":
      return "dashboard.signInForHistory";
    case "unavailable":
      return "dashboard.historyUnavailable";
    case "empty":
      return "history.empty";
    default:
      return null;
  }
}

export function Dashboard() {
  const { t } = useLocale();
  const saved = useSavedCharts();
  const [recent, setRecent] = useState<ChartRef[]>([]);
  const [source, setSource] = useState<HistorySource | "loading">("loading");

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const res = await getHistory();
        if (cancelled) return;
        setRecent(res.items.slice(0, 6));
        setSource(res.source);
      } catch {
        if (!cancelled) {
          setRecent([]);
          setSource("unavailable");
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const statusKey = historyStatusKey(source);

  return (
    <div data-testid="dashboard" className="cs-page cs-reveal">
      <header className="cs-cast-intro">
        <p className="cs-kicker">{t("app.tagline")}</p>
        <h1>{t("dashboard.title")}</h1>
        <p className="cs-lead-short">{t("dashboard.lead")}</p>
      </header>
      <p data-testid="disclaimer" className="visually-hidden">
        {t("disclaimer.short")}
      </p>

      <div className="cs-card cs-dashboard-toolbar">
        <QuickCast />
        <p className="cs-muted cs-dashboard-status" aria-live="polite">
          {statusKey ? t(statusKey) : "…"}
        </p>
      </div>

      <section className="cs-card">
        <RecentCharts
          charts={recent.map((c) => ({
            query_id: c.query_id,
            he: c.he,
            question_type: c.question_type,
            cast_at: c.created_at,
          }))}
          title={t("dashboard.recent")}
        />
      </section>

      <section className="cs-card" data-testid="saved-charts-section">
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
      </section>

      <FlowEntryCards />

      <nav className="cs-muted cs-dashboard-links" aria-label={t("dashboard.title")}>
        <Link href="/cast">{t("dashboard.fullForm")}</Link>
        <span aria-hidden>·</span>
        <Link href="/learn">{t("nav.learn")}</Link>
      </nav>
    </div>
  );
}
