"use client";

import { useMemo, useState } from "react";
import { readThaiAtBan, type LaSoLike } from "../../lib/chart/read-thai-at-ban";
import { useLocale } from "../i18n/locale-provider";

const LOSHU = [4, 9, 2, 3, 5, 7, 8, 1, 6];

const TUONG_KEYS: Record<string, string> = {
  chu_dai_tuong: "chart.taiyi.chuDai",
  chu_tham_tuong: "chart.taiyi.chuTham",
  khach_dai_tuong: "chart.taiyi.khachDai",
  khach_tham_tuong: "chart.taiyi.khachTham",
  ke_than: "chart.taiyi.keThan",
  thuy_kich: "chart.taiyi.thuyKich",
  van_xuong: "chart.taiyi.vanXuong",
  chu_toan: "chart.taiyi.chuToan",
  khach_toan: "chart.taiyi.khachToan",
  chu_truong_doan: "chart.taiyi.chuTruongDoan",
  khach_truong_doan: "chart.taiyi.khachTruongDoan",
};

/**
 * TaiYi chart view — FR-CHART-003. Pure reader of he=thai_at ban.
 * Center palace is marked skip (not used for Tai Yi station).
 */
export function TaiyiChart({ laso }: { laso: LaSoLike }) {
  const { t } = useLocale();
  const { ban } = useMemo(() => readThaiAtBan(laso), [laso]);
  const [selected, setSelected] = useState<number | null>(null);
  const thaiAt = ban.thai_at_cung ?? null;
  const than = ban.thap_luc_than ?? [];
  const tuong = ban.bat_tuong ?? {};
  const toan = ban.cac_toan ?? {};

  return (
    <div
      data-testid="taiyi-chart"
      aria-label={t("system.thai_at")}
      style={{ display: "grid", gap: 16 }}
    >
      <section>
        <h3>{t("chart.taiyi.ninePalace")}</h3>
        <div
          role="grid"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, minmax(72px, 1fr))",
            gap: 6,
            maxWidth: 360,
          }}
        >
          {LOSHU.map((p) => {
            const isThai = thaiAt === p;
            const isCenter = p === 5;
            const sel = selected === p;
            return (
              <button
                key={p}
                type="button"
                role="gridcell"
                data-palace={p}
                data-thai-at={isThai || undefined}
                aria-label={
                  isThai
                    ? `${t("palace.label", { n: p })} · ${t("system.thai_at")}`
                    : t("palace.label", { n: p })
                }
                aria-pressed={sel}
                onClick={() => setSelected(p)}
                style={{
                  minHeight: 72,
                  border: isThai
                    ? "2px solid var(--color-ochre, #c4a35a)"
                    : sel
                      ? "2px solid var(--color-border)"
                      : "1px solid var(--color-border)",
                  borderRadius: 6,
                  background: isCenter
                    ? "var(--color-surface)"
                    : "var(--color-bg, #fff)",
                  opacity: isCenter ? 0.65 : 1,
                  fontSize: 12,
                  cursor: "pointer",
                  fontFamily: "inherit",
                }}
              >
                <div>
                  {t("chart.palace")} {p}
                </div>
                {isThai && (
                  <div data-testid="thai-at-marker" style={{ fontWeight: 700 }}>
                    {t("system.thai_at")}
                  </div>
                )}
                {isCenter && (
                  <div className="cs-muted">{t("chart.taiyi.centerSkip")}</div>
                )}
              </button>
            );
          })}
        </div>
      </section>

      <section>
        <h3>{t("chart.taiyi.sixteenGods")}</h3>
        <div
          data-testid="muoi-sau-than-ring"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, minmax(64px, 1fr))",
            gap: 6,
          }}
        >
          {(than.length
            ? than
            : Array.from({ length: 16 }, (_, i) => ({
                ring: i,
                chi: undefined as string | undefined,
                han: undefined as string | undefined,
                loai: undefined as string | undefined,
              }))
          ).map((item, i) => (
            <div
              key={i}
              tabIndex={0}
              className="cs-card"
              style={{ padding: 8, fontSize: 11 }}
            >
              <div style={{ fontFamily: "serif", fontWeight: 600 }}>
                {item.han ?? item.chi ?? `${t("chart.taiyi.ring")} ${item.ring ?? i}`}
              </div>
              <div className="cs-muted">
                {String(item.loai ?? "").toLowerCase().includes("gian")
                  ? t("chart.taiyi.gianThan")
                  : t("chart.taiyi.chinhCung")}
              </div>
              {item.chi ? (
                <div style={{ fontFamily: "serif" }}>{item.chi}</div>
              ) : null}
            </div>
          ))}
        </div>
      </section>

      <section data-testid="bat-tuong">
        <h3>{t("chart.taiyi.generalsCalc")}</h3>
        <ul style={{ fontSize: 13, listStyle: "none", padding: 0, margin: 0 }}>
          {[...Object.entries(tuong), ...Object.entries(toan)].map(([k, v]) => {
            let display = String(v);
            if (display === "truong") display = t("chart.taiyi.long");
            if (display === "doan") display = t("chart.taiyi.short");
            return (
              <li
                key={k}
                className="cs-pattern-row"
                style={{ marginBottom: 6 }}
              >
                <span>{TUONG_KEYS[k] ? t(TUONG_KEYS[k]) : k}</span>
                <strong>{display}</strong>
              </li>
            );
          })}
        </ul>
      </section>
    </div>
  );
}
