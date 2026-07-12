"use client";

import { useMemo, useState } from "react";
import type { ChartRef } from "../../lib/api/history";
import { shareChart } from "../../lib/api/history";
import { useLocale } from "../i18n/locale-provider";
import { ExportMenu } from "./export-menu";
import { ShareDialog } from "./share-dialog";

/** Saved-chart history — filterable, links to results/report. Read-only. */
export function HistoryList({ items }: { items: ChartRef[] }) {
  const { t } = useLocale();
  const [he, setHe] = useState<string>("");
  const [qtype, setQtype] = useState<string>("");
  const [shareUrl, setShareUrl] = useState<string | null>(null);

  const filtered = useMemo(() => {
    return items.filter((it) => {
      if (he && it.he !== he) return false;
      if (qtype && it.question_type !== qtype) return false;
      return true;
    });
  }, [items, he, qtype]);

  return (
    <div data-testid="history-list" className="cs-card">
      <div style={{ display: "flex", gap: 8, marginBottom: 12, flexWrap: "wrap" }}>
        <label>
          {t("history.filterSystem")}
          <select
            data-testid="filter-he"
            value={he}
            onChange={(e) => setHe(e.target.value)}
          >
            <option value="">{t("history.all")}</option>
            <option value="ky_mon">{t("system.ky_mon")}</option>
            <option value="luc_nham">{t("system.luc_nham")}</option>
            <option value="thai_at">{t("system.thai_at")}</option>
          </select>
        </label>
        <label>
          {t("history.filterQuestion")}
          <select
            data-testid="filter-qtype"
            value={qtype}
            onChange={(e) => setQtype(e.target.value)}
          >
            <option value="">{t("history.all")}</option>
            <option value="trach_thoi">{t("cast.q.trach_thoi")}</option>
            <option value="chu_khach">{t("cast.q.chu_khach")}</option>
            <option value="phuong_vi">{t("cast.q.phuong_vi")}</option>
          </select>
        </label>
      </div>
      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {filtered.map((it) => (
          <li
            key={it.query_id}
            data-testid="history-row"
            style={{
              padding: "12px 0",
              borderBottom: "1px solid var(--color-border)",
              display: "flex",
              flexWrap: "wrap",
              gap: 8,
              alignItems: "center",
            }}
          >
            <a href={`/results/${it.query_id}`}>
              {t("history.resultsLink")} {it.query_id}
            </a>
            {it.report_id ? (
              <>
                {" · "}
                <a href={`/report/${it.report_id}`}>{t("history.reportLink")}</a>
              </>
            ) : null}
            <span className="cs-muted">
              {t(`system.${it.he}`).startsWith("[missing:")
                ? it.he
                : t(`system.${it.he}`)}
              {" · "}
              {t(`cast.q.${it.question_type}`).startsWith("[missing:")
                ? it.question_type
                : t(`cast.q.${it.question_type}`)}
            </span>
            <button
              type="button"
              data-testid="share-btn"
              onClick={async () => {
                const { url } = await shareChart(it.query_id);
                setShareUrl(url);
              }}
            >
              {t("history.share")}
            </button>
            <ExportMenu queryId={it.query_id} reportId={it.report_id} />
          </li>
        ))}
      </ul>
      {shareUrl ? (
        <ShareDialog url={shareUrl} onClose={() => setShareUrl(null)} />
      ) : null}
    </div>
  );
}
