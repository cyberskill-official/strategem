"use client";

export function TamTruyenView({
  so,
  trung,
  mat,
  phap,
}: {
  so?: string;
  trung?: string;
  mat?: string;
  phap?: string;
}) {
  const rows = [
    { label: "初傳", chi: so },
    { label: "中傳", chi: trung },
    { label: "末傳", chi: mat },
  ];
  return (
    <div data-testid="tam-truyen">
      {phap && (
        <p style={{ fontSize: 12, opacity: 0.8 }}>法 {phap}</p>
      )}
      <ol style={{ paddingLeft: 20, margin: 0 }}>
        {rows.map((r) => (
          <li key={r.label} tabIndex={0} style={{ marginBottom: 4 }}>
            <strong>{r.label}</strong> {r.chi ?? "—"}
          </li>
        ))}
      </ol>
    </div>
  );
}
