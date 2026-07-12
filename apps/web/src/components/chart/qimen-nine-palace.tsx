"use client";

/**
 * Interactive 9-palace QiMen chart — FR-CHART-001.
 * Reads envelope ban read-only; never re-computes plates.
 */

import { displayDomainTerm } from "../../lib/domain/glossary";
import { useLocale } from "../i18n/locale-provider";

export type PalaceCell = {
  palace: number;
  stem?: string;
  star?: string;
  door?: string | null;
  god?: string | null;
  highlight?: boolean;
};

export type QimenChartProps = {
  ban?: {
    dia_ban?: string[];
    thien_ban?: string[];
    cuu_tinh?: string[];
    bat_mon?: (string | null)[];
    bat_than?: (string | null)[];
    dinh_cuc?: { so_cuc?: number; duong_don?: boolean };
  };
  selectedPalace?: number | null;
  onSelectPalace?: (palace: number) => void;
  labels?: Record<number, string>;
};

const LOSHU_ORDER = [4, 9, 2, 3, 5, 7, 8, 1, 6];

export function cellsFromBan(ban: QimenChartProps["ban"]): PalaceCell[] {
  const cells: PalaceCell[] = [];
  for (let p = 1; p <= 9; p++) {
    const i = p - 1;
    cells.push({
      palace: p,
      stem: ban?.thien_ban?.[i] ?? ban?.dia_ban?.[i],
      star: ban?.cuu_tinh?.[i],
      door: ban?.bat_mon?.[i] ?? null,
      god: ban?.bat_than?.[i] ?? null,
    });
  }
  return cells;
}

export function QimenNinePalace({
  ban,
  selectedPalace = null,
  onSelectPalace,
}: QimenChartProps) {
  const { t, locale } = useLocale();
  const cells = cellsFromBan(ban);
  const byPalace = new Map(cells.map((c) => [c.palace, c]));

  return (
    <div
      role="grid"
      aria-label={t("system.ky_mon")}
      data-testid="qimen-nine-palace"
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, minmax(88px, 1fr))",
        gap: "var(--space-2, 8px)",
        maxWidth: 440,
      }}
    >
      {LOSHU_ORDER.map((p) => {
        const cell = byPalace.get(p)!;
        const selected = selectedPalace === p;
        const star = displayDomainTerm(cell.star, locale);
        const door = displayDomainTerm(cell.door, locale);
        const god = displayDomainTerm(cell.god, locale);
        return (
          <button
            key={p}
            type="button"
            role="gridcell"
            aria-label={t("palace.label", { n: p })}
            aria-pressed={selected}
            data-palace={p}
            onClick={() => onSelectPalace?.(p)}
            style={{
              minHeight: 104,
              border: selected
                ? "2px solid var(--color-ochre, #c4a35a)"
                : "1px solid var(--color-border, #ccc)",
              borderRadius: "var(--radius-md, 8px)",
              padding: 10,
              textAlign: "left",
              cursor: "pointer",
              fontSize: 12,
              fontFamily: "inherit",
              lineHeight: 1.45,
            }}
          >
            <div style={{ fontWeight: 700, color: "var(--cs-color-brand-umber)", marginBottom: 4 }}>
              {t("chart.palace")} {p}
            </div>
            {cell.stem ? (
              <div>
                <span className="cs-muted">{t("chart.stem")}</span>{" "}
                <span style={{ fontFamily: "serif", fontSize: 14 }}>{cell.stem}</span>
              </div>
            ) : null}
            {star ? (
              <div>
                <span className="cs-muted">{t("chart.star")}</span> {star}
              </div>
            ) : null}
            {door ? (
              <div>
                <span className="cs-muted">{t("chart.door")}</span> {door}
              </div>
            ) : null}
            {god ? (
              <div>
                <span className="cs-muted">{t("chart.god")}</span> {god}
              </div>
            ) : null}
          </button>
        );
      })}
      {ban?.dinh_cuc ? (
        <div
          style={{ gridColumn: "1 / -1", fontSize: 13, opacity: 0.85, fontWeight: 550 }}
          data-testid="dinh-cuc-summary"
        >
          局 {ban.dinh_cuc.so_cuc}
          {ban.dinh_cuc.duong_don === false ? " · 陰遁" : " · 陽遁"}
        </div>
      ) : null}
    </div>
  );
}
