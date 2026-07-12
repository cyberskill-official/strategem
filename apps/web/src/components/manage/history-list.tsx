"use client";

import { useMemo, useState } from "react";
import type { ChartRef } from "../../lib/api/history";
import { shareChart } from "../../lib/api/history";
import { ExportMenu } from "./export-menu";
import { ShareDialog } from "./share-dialog";

/** Saved-chart history — filterable, links to results/report. Read-only. */
export function HistoryList({ items }: { items: ChartRef[] }) {
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
    <div data-testid="history-list">
      <div style={{ display: "flex", gap: 8, marginBottom: 12 }}>
        <label>
          System{" "}
          <select
            data-testid="filter-he"
            value={he}
            onChange={(e) => setHe(e.target.value)}
          >
            <option value="">All</option>
            <option value="ky_mon">QiMen</option>
            <option value="luc_nham">LiuRen</option>
            <option value="thai_at">TaiYi</option>
          </select>
        </label>
        <label>
          Question{" "}
          <select
            data-testid="filter-qtype"
            value={qtype}
            onChange={(e) => setQtype(e.target.value)}
          >
            <option value="">All</option>
            <option value="trach_thoi">trach_thoi</option>
            <option value="chu_khach">chu_khach</option>
            <option value="phuong_vi">phuong_vi</option>
          </select>
        </label>
      </div>
      <ul>
        {filtered.map((it) => (
          <li key={it.query_id} data-testid="history-row">
            <a href={`/results/${it.query_id}`}>Results {it.query_id}</a>
            {it.report_id ? (
              <>
                {" · "}
                <a href={`/report/${it.report_id}`}>Report</a>
              </>
            ) : null}
            <span style={{ marginLeft: 8, opacity: 0.7 }}>
              {it.he} · {it.question_type}
            </span>
            <button
              type="button"
              data-testid="share-btn"
              onClick={async () => {
                const { url } = await shareChart(it.query_id);
                setShareUrl(url);
              }}
            >
              Share
            </button>
            <ExportMenu
              queryId={it.query_id}
              reportId={it.report_id}
            />
          </li>
        ))}
      </ul>
      {shareUrl ? (
        <ShareDialog url={shareUrl} onClose={() => setShareUrl(null)} />
      ) : null}
    </div>
  );
}
