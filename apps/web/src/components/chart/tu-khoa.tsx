"use client";

export type KhoaPair = { thuong: string; ha: string; khac?: string | null };

export function TuKhoaView({ khoa }: { khoa: KhoaPair[] }) {
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
          style={{
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            padding: 8,
            minWidth: 72,
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: 11, opacity: 0.7 }}>課 {i + 1}</div>
          <div>上 {k.thuong}</div>
          <div>下 {k.ha}</div>
          {k.khac && (
            <div style={{ fontSize: 11 }}>
              {k.khac === "ha_khac" || k.khac === "tac" ? "▼ 賊" : "▲ 克"}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
