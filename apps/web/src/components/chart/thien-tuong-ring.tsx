"use client";

const DEFAULT_GENERALS = [
  "貴人",
  "螣蛇",
  "朱雀",
  "六合",
  "勾陳",
  "青龍",
  "天空",
  "白虎",
  "太常",
  "玄武",
  "太陰",
  "天后",
];

export function ThienTuongRing({
  generals,
}: {
  generals?: string[] | Record<string, string>;
}) {
  let list: string[] = DEFAULT_GENERALS;
  if (Array.isArray(generals) && generals.length === 12) {
    list = generals;
  } else if (generals && !Array.isArray(generals)) {
    list = Object.values(generals);
  }

  return (
    <div
      data-testid="thien-tuong-ring"
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, minmax(64px, 1fr))",
        gap: 6,
      }}
    >
      {list.map((g, i) => (
        <div
          key={`${g}-${i}`}
          tabIndex={0}
          style={{
            border: "1px solid var(--color-border)",
            borderRadius: 6,
            padding: 6,
            fontSize: 12,
            textAlign: "center",
          }}
        >
          {g}
        </div>
      ))}
    </div>
  );
}
