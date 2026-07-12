/** Read-only TaiYi ban adapter — FR-CHART-003. */

export type ThaiAtBanView = {
  thai_at_cung?: number;
  thai_at_ring?: number;
  thap_luc_than?: Array<{
    ring?: number;
    chi?: string;
    han?: string;
    loai?: string;
  }>;
  bat_tuong?: Record<string, number | string>;
  cac_toan?: Record<string, number | string>;
  tich?: Record<string, number | string>;
};

export type LaSoLike = {
  he?: string;
  ban?: ThaiAtBanView;
  cach_cuc?: Array<{ polarity?: string; name?: string }>;
};

export function readThaiAtBan(laso: LaSoLike): {
  ban: ThaiAtBanView;
  cachCuc: NonNullable<LaSoLike["cach_cuc"]>;
} {
  if (laso.he && laso.he !== "thai_at") {
    throw new Error(`expected he=thai_at, got ${laso.he}`);
  }
  return { ban: laso.ban ?? {}, cachCuc: laso.cach_cuc ?? [] };
}
