"use client";

import { useLocale } from "../i18n/locale-provider";

export type KhoaPair = { thuong: string; ha: string; khac?: string | null };

export function TuKhoaView({ khoa }: { khoa: KhoaPair[] }) {
  const { t } = useLocale();
  const items: KhoaPair[] =
    khoa.length > 0
      ? khoa
      : Array.from({ length: 4 }, () => ({ thuong: "—", ha: "—", khac: null }));

  return (
    <div data-testid="tu-khoa" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {items.map((k, i) => (
        <div
          key={i}
          tabIndex={0}
          data-khoa={i + 1}
          className="cs-card"
          style={{
            padding: 10,
            minWidth: 80,
            textAlign: "center",
          }}
        >
          <div className="cs-muted" style={{ fontSize: 11 }}>
            {t("chart.liuren.khoaN", { n: i + 1 })}
          </div>
          <div style={{ fontFamily: "serif", fontSize: 16 }}>
            {t("chart.liuren.upper")} {k.thuong}
          </div>
          <div style={{ fontFamily: "serif", fontSize: 16 }}>
            {t("chart.liuren.lower")} {k.ha}
          </div>
          {k.khac ? (
            <div style={{ fontSize: 11 }}>
              {k.khac === "ha_khac" || k.khac === "tac"
                ? t("chart.liuren.thief")
                : t("chart.liuren.conquer")}
            </div>
          ) : null}
        </div>
      ))}
    </div>
  );
}
