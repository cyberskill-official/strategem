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
            : source === "unauthorized"
              ? t("dashboard.signInForHistory")
              : source === "unavailable"
                ? t("dashboard.historyUnavailable")
                : source === "empty"
                  ? t("history.empty")
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
