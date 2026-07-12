/** Read-only adapter for LiuRen chart (FR-CHART-002). */

export type LucNhamBan = {
  thien_dia_ban?: {
    dia?: string[];
    thien?: string[];
    dia_ban?: string[];
    thien_ban?: string[];
    nguyet_tuong?: string;
    gio_chiem?: string;
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
