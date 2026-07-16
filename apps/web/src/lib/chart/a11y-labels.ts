/** Screen-reader labels for chart components — TASK-CHART-004. */

export function palaceLabel(palace: number, content: string[]): string {
  const body = content.filter(Boolean).join(", ") || "empty";
  return `Palace ${palace}: ${body}`;
}

export function polarityLabel(polarity: string): string {
  const p = polarity.toLowerCase();
  if (p === "cat") return "Auspicious (cát)";
  if (p === "hung") return "Inauspicious (hung)";
  return "Neutral (trung)";
}

export function diacriticSample(): string[] {
  // Vietnamese stacked diacritics + Han for clip tests
  return ["huyền", "ngã", "nặng", "ấ", "ộ", "青龍返首", "貴人"];
}
