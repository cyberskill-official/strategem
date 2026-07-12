"use client";

export type PatternItem = {
  id?: string;
  name: string;
  cung?: number | null;
  polarity?: string;
  score?: number | null;
  citations?: string[];
};

function PolarityBadge({ polarity }: { polarity?: string }) {
  const p = (polarity ?? "trung").toLowerCase();
  const label = p === "cat" ? "Cát" : p === "hung" ? "Hung" : "Trung";
  const icon = p === "cat" ? "▲" : p === "hung" ? "▼" : "◆";
  // icon + text, never color alone
  return (
    <span
      data-testid="polarity-badge"
      style={{
        display: "inline-flex",
        gap: 4,
        alignItems: "center",
        fontSize: 12,
        padding: "2px 8px",
        borderRadius: 999,
        border: "1px solid var(--color-border)",
      }}
      aria-label={`Polarity ${label}`}
    >
      <span aria-hidden>{icon}</span>
      <span>{label}</span>
    </span>
  );
}

export function PatternList({ patterns }: { patterns: PatternItem[] }) {
  if (!patterns.length) {
    return <p data-testid="patterns-empty">No patterns detected.</p>;
  }
  return (
    <ul data-testid="pattern-list" style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {patterns.map((p, i) => (
        <li
          key={p.id ?? `${p.name}-${i}`}
          style={{
            display: "flex",
            justifyContent: "space-between",
            gap: 8,
            padding: "8px 0",
            borderBottom: "1px solid var(--color-border)",
          }}
        >
          <div>
            <strong>{p.name}</strong>
            {p.cung != null && (
              <span style={{ marginLeft: 8, opacity: 0.8 }}>cung {p.cung}</span>
            )}
          </div>
          <PolarityBadge polarity={p.polarity} />
        </li>
      ))}
    </ul>
  );
}
