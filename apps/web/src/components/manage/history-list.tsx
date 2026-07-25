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
      <div className="cs-table-wrap">
        <table className="cs-table">
          <thead>
            <tr>
              <th scope="col">{t("history.resultsLink")}</th>
              <th scope="col">{t("history.filterSystem")}</th>
              <th scope="col">{t("history.filterQuestion")}</th>
              <th scope="col" aria-label={t("history.share")} />
            </tr>
          </thead>
          <tbody>
            {filtered.map((it) => (
              <tr key={it.query_id} data-testid="history-row">
                <td>
                  <a href={`/results/${it.query_id}`}>
                    {t("history.resultsLink")} {it.query_id}
                  </a>
                  {it.report_id ? (
                    <>
                      {" · "}
                      <a href={`/report/${it.report_id}`}>{t("history.reportLink")}</a>
                    </>
                  ) : null}
                </td>
                <td>
                  <span className="cs-badge cs-badge--trung">
                    {t(`system.${it.he}`).startsWith("[missing:")
                      ? it.he
                      : t(`system.${it.he}`)}
                  </span>
                </td>
                <td className="cs-muted">
                  {t(`cast.q.${it.question_type}`).startsWith("[missing:")
                    ? it.question_type
                    : t(`cast.q.${it.question_type}`)}
                </td>
                <td>
                  <span style={{ display: "inline-flex", gap: 8, alignItems: "center" }}>
                    <button
                      type="button"
                      className="cs-button cs-button--secondary cs-button--xs"
                      data-testid="share-btn"
                      onClick={async () => {
                        const { url } = await shareChart(it.query_id);
                        setShareUrl(url);
                      }}
                    >
                      {t("history.share")}
                    </button>
                    <ExportMenu queryId={it.query_id} reportId={it.report_id} />
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {shareUrl ? (
        <ShareDialog url={shareUrl} onClose={() => setShareUrl(null)} />
      ) : null}
    </div>
  );
}
