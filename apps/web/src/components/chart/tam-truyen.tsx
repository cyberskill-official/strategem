"use client";

import { useLocale } from "../i18n/locale-provider";

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
  const { t } = useLocale();
  const rows = [
    { label: t("chart.liuren.truyenSo"), chi: so },
    { label: t("chart.liuren.truyenTrung"), chi: trung },
    { label: t("chart.liuren.truyenMat"), chi: mat },
  ];
  return (
    <div data-testid="tam-truyen">
      {phap ? (
        <p className="cs-muted" style={{ fontSize: 13 }}>
          {t("chart.liuren.method")} <strong>{phap}</strong>
        </p>
      ) : null}
      <ol style={{ paddingLeft: 20, margin: 0 }}>
        {rows.map((r) => (
          <li key={r.label} tabIndex={0} style={{ marginBottom: 6 }}>
            <strong>{r.label}</strong>{" "}
            <span style={{ fontFamily: "serif", fontSize: 17 }}>
              {r.chi ?? "—"}
            </span>
          </li>
        ))}
      </ol>
    </div>
  );
}
