"use client";

import { useLocale } from "../i18n/locale-provider";

/**
 * Interactive 9-palace QiMen chart — FR-CHART-001.
 * Reads envelope ban read-only; never re-computes plates.
 */

export type PalaceCell = {
  palace: number; // 1..9
  stem?: string;
  star?: string;
  door?: string | null;
  god?: string | null;
  highlight?: boolean;
};

export type QimenChartProps = {
  /** ban from la so envelope (he=ky_mon) */
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
  /** Lo Shu visual order: 4 9 2 / 3 5 7 / 8 1 6 */
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
  const { t } = useLocale();
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
        maxWidth: 420,
      }}
    >
      {LOSHU_ORDER.map((p) => {
        const cell = byPalace.get(p)!;
        const selected = selectedPalace === p;
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
              minHeight: 96,
              border: selected
                ? "2px solid var(--color-ochre, #c4a35a)"
                : "1px solid var(--color-border, #ccc)",
              borderRadius: "var(--radius-md, 8px)",
              background: "var(--color-surface, #fff)",
              padding: 8,
              textAlign: "left",
              cursor: "pointer",
              fontSize: 12,
              fontFamily: "inherit",
            }}
          >
            <div style={{ fontWeight: 600 }}>
              {t("chart.palace")} {p}
            </div>
            {cell.stem && (
              <div>
                {t("chart.stem")} {cell.stem}
              </div>
            )}
            {cell.star && (
              <div>
                {t("chart.star")} {cell.star}
              </div>
            )}
            {cell.door && (
              <div>
                {t("chart.door")} {cell.door}
              </div>
            )}
            {cell.god && (
              <div>
                {t("chart.god")} {cell.god}
              </div>
            )}
          </button>
        );
      })}
      {ban?.dinh_cuc && (
        <div
          style={{ gridColumn: "1 / -1", fontSize: 12, opacity: 0.8 }}
          data-testid="dinh-cuc-summary"
        >
          局 {ban.dinh_cuc.so_cuc}
          {ban.dinh_cuc.duong_don === false ? " · 陰遁" : " · 陽遁"}
        </div>
      )}
    </div>
  );
}
