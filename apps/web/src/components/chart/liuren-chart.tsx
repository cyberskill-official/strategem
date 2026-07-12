"use client";

import { useMemo, useState } from "react";
import {
  readLucNhamBan,
  resolveThienDiaBan,
  type LaSoLike,
} from "../../lib/chart/read-luc-nham-ban";
import { displayDomainTerm } from "../../lib/domain/glossary";
import { useLocale } from "../i18n/locale-provider";
import { TamTruyenView } from "./tam-truyen";
import { ThienDiaBanView } from "./thien-dia-ban";
import { ThienTuongRing } from "./thien-tuong-ring";
import { TuKhoaView, type KhoaPair } from "./tu-khoa";

/**
 * Interactive LiuRen chart — FR-CHART-002.
 * Pure reader of he=luc_nham ban; never re-computes plates.
 * If thien_dia arrays are missing, aligns heaven from stamped 月将+占时 only.
 */
export function LiurenChart({ laso }: { laso: LaSoLike }) {
  const { t, locale } = useLocale();
  const { ban } = useMemo(() => readLucNhamBan(laso), [laso]);
  const [selected, setSelected] = useState<number | null>(null);

  const plate = useMemo(() => resolveThienDiaBan(ban), [ban]);

  const khoa: KhoaPair[] = useMemo(() => {
    const raw = ban.tu_khoa ?? [];
    return raw.map((k): KhoaPair => {
      if (Array.isArray(k)) {
        return { thuong: k[0] ?? "—", ha: k[1] ?? "—", khac: null };
      }
      return {
        thuong: k.thuong ?? "—",
        ha: k.ha ?? "—",
        khac: null,
      };
    });
  }, [ban.tu_khoa]);

  const tt = ban.tam_truyen ?? {};

  const generals = useMemo(() => {
    const g = ban.thien_tuong;
    if (Array.isArray(g)) {
      return g.map((name) => displayDomainTerm(name, locale) || name);
    }
    if (g && typeof g === "object") {
      return Object.values(g).map(
        (name) => displayDomainTerm(String(name), locale) || String(name),
      );
    }
    return g;
  }, [ban.thien_tuong, locale]);

  const stateLabel = (() => {
    const s = (plate.state ?? tt.phap ?? "").toLowerCase();
    if (s.includes("phuc")) return t("chart.liuren.statePhuc");
    if (s.includes("phan")) return t("chart.liuren.statePhan");
    if (s.includes("thuong")) return t("chart.liuren.stateThuong");
    if (tt.phap) return displayDomainTerm(tt.phap, locale) || tt.phap;
    return null;
  })();

  return (
    <div
      data-testid="liuren-chart"
      style={{ display: "grid", gap: 16 }}
      aria-label={t("system.luc_nham")}
    >
      {plate.derived ? (
        <div className="cs-banner cs-banner--info" data-testid="liuren-derived-banner">
          {t("chart.liuren.derivedNote")}
        </div>
      ) : null}

      <section>
        <h3>{t("chart.liuren.thienDia")}</h3>
        <ThienDiaBanView
          dia={plate.dia}
          thien={plate.thien}
          nguyetTuong={plate.nguyetTuong}
          gioChiem={plate.gioChiem}
          selected={selected}
          onSelect={setSelected}
        />
        {stateLabel ? (
          <p className="cs-muted" style={{ marginTop: 8 }}>
            {t("chart.liuren.boardState")}: <strong>{stateLabel}</strong>
          </p>
        ) : null}
      </section>
      <section>
        <h3>{t("chart.liuren.tuKhoa")}</h3>
        <TuKhoaView khoa={khoa} />
      </section>
      <section>
        <h3>{t("chart.liuren.tamTruyen")}</h3>
        <TamTruyenView
          so={tt.so}
          trung={tt.trung}
          mat={tt.mat}
          phap={
            tt.phap
              ? displayDomainTerm(tt.phap, locale) || tt.phap
              : tt.phap
          }
        />
      </section>
      <section>
        <h3>{t("chart.liuren.thienTuong")}</h3>
        <ThienTuongRing generals={generals} />
      </section>
    </div>
  );
}
