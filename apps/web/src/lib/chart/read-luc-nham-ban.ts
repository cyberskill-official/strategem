/** Read-only adapter for LiuRen chart (TASK-CHART-002). */

export type LucNhamBan = {
  thien_dia_ban?: {
    dia?: string[];
    thien?: string[];
    dia_ban?: string[];
    thien_ban?: string[];
    nguyet_tuong?: string;
    gio_chiem?: string;
    state?: string;
  };
  tu_khoa?: Array<string[] | { thuong?: string; ha?: string }>;
  tam_truyen?: {
    so?: string;
    trung?: string;
    mat?: string;
    phap?: string;
  };
  thien_tuong?: string[] | Record<string, string>;
  khoa_the?: string[];
  nguyet_tuong?: string;
  gio_chiem?: string;
};

export type LaSoLike = {
  he?: string;
  ban?: LucNhamBan;
  cach_cuc?: Array<{ cung?: number; polarity?: string; name?: string }>;
};

const CHI12 = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"];

/**
 * Derive heaven plate from month general + hour (classical 月将加占时).
 * Used only when envelope omits thien_dia_ban arrays — same formula as
 * crates/cyberos-luchnham quay_thien_ban, applied to already-stamped fields.
 * Does not re-compute tu_khoa / tam_truyen.
 */
export function deriveThienDia(
  nguyetTuong?: string,
  gioChiem?: string,
): { dia: string[]; thien: string[]; derived: boolean } {
  const dia = CHI12.slice();
  if (!nguyetTuong || !gioChiem) {
    return { dia, thien: dia.slice(), derived: false };
  }
  const nt = CHI12.indexOf(nguyetTuong);
  const gc = CHI12.indexOf(gioChiem);
  if (nt < 0 || gc < 0) {
    return { dia, thien: dia.slice(), derived: false };
  }
  // offset = (nguyet_tuong - gio_chiem) mod 12 — matches Rust quay_thien_ban
  const offset = (nt - gc + 12) % 12;
  const thien = dia.map((_, i) => dia[(i + offset) % 12]);
  return { dia, thien, derived: true };
}

export function resolveThienDiaBan(ban: LucNhamBan): {
  dia: string[];
  thien: string[];
  nguyetTuong?: string;
  gioChiem?: string;
  state?: string;
  derived: boolean;
} {
  const tdb = ban.thien_dia_ban ?? {};
  const diaRaw = tdb.dia ?? tdb.dia_ban;
  const thienRaw = tdb.thien ?? tdb.thien_ban;
  const nguyetTuong = ban.nguyet_tuong ?? tdb.nguyet_tuong;
  const gioChiem = ban.gio_chiem ?? tdb.gio_chiem;

  if (diaRaw?.length === 12 && thienRaw?.length === 12) {
    return {
      dia: diaRaw,
      thien: thienRaw,
      nguyetTuong,
      gioChiem,
      state: tdb.state,
      derived: false,
    };
  }

  const derived = deriveThienDia(nguyetTuong, gioChiem);
  return {
    dia: derived.dia,
    thien: derived.thien,
    nguyetTuong,
    gioChiem,
    state: tdb.state,
    derived: derived.derived,
  };
}

export function readLucNhamBan(laso: LaSoLike): {
  ban: LucNhamBan;
  cachCuc: NonNullable<LaSoLike["cach_cuc"]>;
} {
  if (laso.he && laso.he !== "luc_nham") {
    throw new Error(`expected he=luc_nham, got ${laso.he}`);
  }
  return {
    ban: laso.ban ?? {},
    cachCuc: laso.cach_cuc ?? [],
  };
}
