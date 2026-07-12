"use client";

import { useMemo, useState } from "react";
import { displayDomainTerm } from "../../lib/domain/glossary";
import { readLucNhamBan, type LaSoLike } from "../../lib/chart/read-luc-nham-ban";
import { useLocale } from "../i18n/locale-provider";
import { TamTruyenView } from "./tam-truyen";
import { ThienDiaBanView } from "./thien-dia-ban";
import { ThienTuongRing } from "./thien-tuong-ring";
import { TuKhoaView, type KhoaPair } from "./tu-khoa";

/**
 * Interactive LiuRen chart — FR-CHART-002.
 * Pure reader of he=luc_nham ban; never re-computes plates.
 */
export function LiurenChart({ laso }: { laso: LaSoLike }) {
  const { t, locale } = useLocale();
  const { ban } = useMemo(() => readLucNhamBan(laso), [laso]);
  const [selected, setSelected] = useState<number | null>(null);

  const tdb = ban.thien_dia_ban ?? {};
  const dia = tdb.dia ?? tdb.dia_ban;
  const thien = tdb.thien ?? tdb.thien_ban;

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
      return Object.values(g).map((name) =>
        displayDomainTerm(String(name), locale) || String(name),
      );
    }
    return g;
  }, [ban.thien_tuong, locale]);

  return (
    <div
      data-testid="liuren-chart"
      style={{ display: "grid", gap: 16 }}
      aria-label={t("system.luc_nham")}
    >
      <section>
        <h3>{t("chart.liuren.thienDia")}</h3>
        <ThienDiaBanView
          dia={dia}
          thien={thien}
          nguyetTuong={ban.nguyet_tuong ?? tdb.nguyet_tuong}
          gioChiem={ban.gio_chiem ?? tdb.gio_chiem}
          selected={selected}
          onSelect={setSelected}
        />
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
