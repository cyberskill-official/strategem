"use client";

import { useMemo, useState } from "react";
import { readLucNhamBan, type LaSoLike } from "../../lib/chart/read-luc-nham-ban";
import { TamTruyenView } from "./tam-truyen";
import { ThienDiaBanView } from "./thien-dia-ban";
import { ThienTuongRing } from "./thien-tuong-ring";
import { TuKhoaView, type KhoaPair } from "./tu-khoa";

/**
 * Interactive LiuRen chart — FR-CHART-002.
 * Pure reader of he=luc_nham ban; never re-computes plates.
 */
export function LiurenChart({ laso }: { laso: LaSoLike }) {
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

  return (
    <div
      data-testid="liuren-chart"
      style={{ display: "grid", gap: 16 }}
      aria-label="LiuRen chart"
    >
      <section>
        <h3>天地盤</h3>
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
        <h3>四課</h3>
        <TuKhoaView khoa={khoa} />
      </section>
      <section>
        <h3>三傳</h3>
        <TamTruyenView
          so={tt.so}
          trung={tt.trung}
          mat={tt.mat}
          phap={tt.phap}
        />
      </section>
      <section>
        <h3>十二天將</h3>
        <ThienTuongRing generals={ban.thien_tuong} />
      </section>
    </div>
  );
}
