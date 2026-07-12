"use client";

import { useLocale } from "../i18n/locale-provider";

const CHI12 = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

export function ThienDiaBanView({
  dia,
  thien,
  nguyetTuong,
  gioChiem,
  selected,
  onSelect,
}: {
  dia?: string[];
  thien?: string[];
  nguyetTuong?: string;
  gioChiem?: string;
  selected?: number | null;
  onSelect?: (i: number) => void;
}) {
  const { t } = useLocale();
  const earth = dia?.length === 12 ? dia : CHI12;
  const heaven = thien?.length === 12 ? thien : CHI12;

  return (
    <div data-testid="thien-dia-ban">
      <p className="cs-muted" style={{ fontSize: 13, marginBottom: 10 }}>
        {t("chart.liuren.monthGen")}{" "}
        <strong style={{ fontFamily: "serif", fontSize: 16 }}>
          {nguyetTuong ?? "—"}
        </strong>
        {" · "}
        {t("chart.liuren.hour")}{" "}
        <strong style={{ fontFamily: "serif", fontSize: 16 }}>
          {gioChiem ?? "—"}
        </strong>
      </p>
      <div
        role="list"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(6, minmax(48px, 1fr))",
          gap: 6,
        }}
      >
        {earth.map((d, i) => {
          const sel = selected === i;
          const isHour = gioChiem != null && d === gioChiem;
          const isGen = nguyetTuong != null && heaven[i] === nguyetTuong && isHour;
          return (
            <button
              key={i}
              type="button"
              role="listitem"
              data-index={i}
              aria-label={`${t("chart.liuren.earth")} ${d}, ${t("chart.liuren.heaven")} ${heaven[i]}`}
              aria-pressed={sel}
              onClick={() => onSelect?.(i)}
              style={{
                minHeight: 60,
                border: sel
                  ? "2px solid var(--color-ochre, #c4a35a)"
                  : isHour
                    ? "2px solid var(--cs-color-brand-umber)"
                    : "1px solid var(--color-border)",
                borderRadius: 8,
                background: isGen
                  ? "var(--cs-color-surface-raised)"
                  : "var(--color-surface)",
                fontSize: 12,
                cursor: "pointer",
                fontFamily: "inherit",
              }}
            >
              <div>
                <span className="cs-muted">{t("chart.liuren.earthShort")}</span>{" "}
                <span style={{ fontFamily: "serif", fontSize: 15 }}>{d}</span>
              </div>
              <div>
                <span className="cs-muted">{t("chart.liuren.heavenShort")}</span>{" "}
                <span style={{ fontFamily: "serif", fontSize: 15 }}>
                  {heaven[i]}
                </span>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
