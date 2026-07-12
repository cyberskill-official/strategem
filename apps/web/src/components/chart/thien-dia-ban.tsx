"use client";

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
  const earth = dia?.length === 12 ? dia : CHI12;
  const heaven = thien?.length === 12 ? thien : CHI12;

  return (
    <div data-testid="thien-dia-ban">
      <p style={{ fontSize: 12, opacity: 0.8 }}>
        月將 {nguyetTuong ?? "—"} · 占時 {gioChiem ?? "—"}
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
          return (
            <button
              key={i}
              type="button"
              role="listitem"
              data-index={i}
              aria-label={`Branch ${d}, heaven ${heaven[i]}`}
              aria-pressed={sel}
              onClick={() => onSelect?.(i)}
              style={{
                minHeight: 56,
                border: sel
                  ? "2px solid var(--color-ochre, #c4a35a)"
                  : "1px solid var(--color-border)",
                borderRadius: 6,
                background: "var(--color-surface)",
                fontSize: 12,
                cursor: "pointer",
              }}
            >
              <div>地 {d}</div>
              <div>天 {heaven[i]}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}
