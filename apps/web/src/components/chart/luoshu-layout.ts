/** Fixed Luoshu palace grid: 4 9 2 / 3 5 7 / 8 1 6 */

export const LOSHU_GRID: readonly number[] = [4, 9, 2, 3, 5, 7, 8, 1, 6] as const;

export function palaceArrayIndex(palace: number): number {
  if (palace < 1 || palace > 9) throw new Error("palace 1..9");
  return palace - 1;
}
