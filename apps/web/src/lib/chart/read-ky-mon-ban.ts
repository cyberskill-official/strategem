/** Read-only adapter over la so envelope for QiMen chart (FR-CHART-001). */

export type LaSoLike = {
  he?: string;
  ban?: Record<string, unknown>;
  cach_cuc?: Array<{ cung?: number; polarity?: string; name?: string }>;
};

export function readKyMonBan(laso: LaSoLike) {
  if (laso.he && laso.he !== "ky_mon") {
    throw new Error(`expected he=ky_mon, got ${laso.he}`);
  }
  return {
    ban: laso.ban ?? {},
    cachCuc: laso.cach_cuc ?? [],
  };
}
