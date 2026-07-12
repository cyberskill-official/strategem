"use client";

import { useMemo, useState } from "react";
import { readThaiAtBan, type LaSoLike } from "../../lib/chart/read-thai-at-ban";

const LOSHU = [4, 9, 2, 3, 5, 7, 8, 1, 6];

/**
 * TaiYi chart view — FR-CHART-003. Pure reader of he=thai_at ban.
 */
export function TaiyiChart({ laso }: { laso: LaSoLike }) {
  const { ban } = useMemo(() => readThaiAtBan(laso), [laso]);
  const [selected, setSelected] = useState<number | null>(null);
  const thaiAt = ban.thai_at_cung ?? null;
  const than = ban.thap_luc_than ?? [];
  const tuong = ban.bat_tuong ?? {};
  const toan = ban.cac_toan ?? {};

  return (
    <div data-testid="taiyi-chart" aria-label="TaiYi chart" style={{ display: "grid", gap: 16 }}>
      <section>
        <h3>九宮 · Thái Ất</h3>
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
                aria-label={`Palace ${p}${isThai ? ", Thai At" : ""}`}
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
                  background: isCenter ? "var(--color-surface)" : "var(--color-bg, #fff)",
                  opacity: isCenter ? 0.65 : 1,
                  fontSize: 12,
                  cursor: "pointer",
                }}
              >
                <div>宮 {p}</div>
                {isThai && <div data-testid="thai-at-marker">太乙</div>}
                {isCenter && <div>中 (skip)</div>}
              </button>
            );
          })}
        </div>
      </section>

      <section>
        <h3>十六神</h3>
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
          ).map((t, i) => (
            <div
              key={i}
              tabIndex={0}
              style={{
                border: "1px solid var(--color-border)",
                borderRadius: 6,
                padding: 6,
                fontSize: 11,
              }}
            >
              <div>{t.han ?? t.chi ?? `ring ${t.ring ?? i}`}</div>
              <div style={{ opacity: 0.7 }}>
                {String(t.loai ?? "").toLowerCase().includes("gian")
                  ? "間神"
                  : "正宮"}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section data-testid="bat-tuong">
        <h3>八將 · 算</h3>
        <ul style={{ fontSize: 13 }}>
          {Object.entries(tuong).map(([k, v]) => (
            <li key={k}>
              {k}: {String(v)}
            </li>
          ))}
          {Object.entries(toan).map(([k, v]) => (
            <li key={k}>
              {k}: {String(v)}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
