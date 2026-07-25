/**
 * Ngũ Hành elemental identity per divination system — drives the
 * @cyberskill/design `data-cs-element` theming axis (one element per surface).
 *
 * Mapping rationale (stem associations, VI-first):
 * - Lục Nhâm → thủy: Nhâm (壬) is the yang water stem.
 * - Thái Ất → mộc: Ất (乙) is the yin wood stem.
 * - Kỳ Môn → kim: the military/strategy art — metal, decisiveness.
 * Default (no element) keeps the studio Thổ look.
 */
export type CsElement = "kim" | "moc" | "thuy" | "hoa" | "tho";

export function systemElement(system: string | null | undefined): CsElement | undefined {
  const s = (system ?? "").toLowerCase();
  if (s === "qimen" || s === "ky_mon") return "kim";
  if (s === "liuren" || s === "luc_nham") return "thuy";
  if (s === "taiyi" || s === "thai_at") return "moc";
  return undefined;
}
