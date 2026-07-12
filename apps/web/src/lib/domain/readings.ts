/**
 * Locale-native literary readings for UI when API returns English stubs.
 * Does NOT machine-translate classical text; composes expert-authored templates.
 */

import type { Locale } from "../../i18n/routing";
import { displayPatternName, patternGloss } from "./glossary";

export type ReadingInput = {
  he?: string;
  patterns: Array<{ name?: string; polarity?: string; cung?: number | null }>;
  persona: "beginner" | "expert";
};

const SYSTEM: Record<string, Record<Locale, string>> = {
  ky_mon: { vi: "Kỳ Môn", en: "Qi Men", zh: "奇门" },
  luc_nham: { vi: "Lục Nhâm", en: "Liu Ren", zh: "六壬" },
  thai_at: { vi: "Thái Ất", en: "Tai Yi", zh: "太乙" },
  qimen: { vi: "Kỳ Môn", en: "Qi Men", zh: "奇门" },
};

function systemName(he: string | undefined, locale: Locale): string {
  if (!he) return SYSTEM.ky_mon[locale];
  return SYSTEM[he]?.[locale] ?? he;
}

function isEnglishStub(text: string | undefined | null): boolean {
  if (!text) return true;
  if (/Educational reading for|Technical notes for|Detected patterns:/.test(text))
    return true;
  // Mostly ASCII Latin without Vietnamese diacritics → treat as stub for vi/zh
  const letters = text.replace(/[^A-Za-zÀ-ỹ]/g, "");
  if (letters.length < 20) return false;
  const viMarks = (text.match(/[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/gi) || [])
    .length;
  const cjk = (text.match(/[\u4e00-\u9fff]/g) || []).length;
  if (viMarks + cjk > 8) return false;
  return /[A-Za-z]{12,}/.test(text);
}

export function shouldReplaceReading(
  text: string | undefined | null,
  locale: Locale,
): boolean {
  if (!text) return true;
  if (locale === "en") return isEnglishStub(text);
  // For vi/zh, always replace English stubs
  return isEnglishStub(text);
}

export function composeReading(input: ReadingInput, locale: Locale): string {
  const sys = systemName(input.he, locale);
  const names = input.patterns
    .map((p) => displayPatternName(p.name ?? "", locale))
    .filter(Boolean);
  const unique = [...new Set(names)];
  const glosses = input.patterns
    .map((p) => patternGloss(p.name ?? "", locale))
    .filter(Boolean);
  const uniqueGloss = [...new Set(glosses)];

  if (locale === "vi") {
    if (input.persona === "expert") {
      return [
        `Bàn ${sys} đã định cục. Cách cục quan sát: ${unique.join(" · ") || "chưa có cách nổi bật"}.`,
        uniqueGloss.length
          ? uniqueGloss.map((g) => `• ${g}`).join("\n")
          : "• Chưa có chú giải cách cục bổ sung.",
        "Đọc bàn là khung tham chiếu — không thay cho phán đoán của người hỏi. Cân chủ–khách, thời–thế, rồi mới quyết.",
      ].join("\n\n");
    }
    return [
      `Theo ${sys}, la số đã thành. Những điểm đáng chú ý: ${unique.join(", ") || "bàn êm, ít cách cục nổi"}.`,
      uniqueGloss[0] ? uniqueGloss[0] : "Hãy đọc các cung then chốt trước khi kết luận.",
      "Đây là hỗ trợ suy nghĩ, không phải lời phán. Bạn là người quyết định.",
    ].join("\n\n");
  }

  if (locale === "zh") {
    if (input.persona === "expert") {
      return [
        `${sys}盘局已定。所见格局：${unique.join(" · ") || "无明显格局"}。`,
        uniqueGloss.length
          ? uniqueGloss.map((g) => `• ${g}`).join("\n")
          : "• 暂无补充格局说明。",
        "读盘为参照框架，不能替代问事者的判断。衡主客、时势，而后决。",
      ].join("\n\n");
    }
    return [
      `依${sys}，盘已成。宜留意：${unique.join("、") || "盘势平稳"}。`,
      uniqueGloss[0] ?? "请先读关键宫位再下结论。",
      "此为思考辅助，非裁决。决定权在你。",
    ].join("\n\n");
  }

  // en
  if (input.persona === "expert") {
    return [
      `${sys} board is fixed. Observed patterns: ${unique.join(" · ") || "none prominent"}.`,
      uniqueGloss.length
        ? uniqueGloss.map((g) => `• ${g}`).join("\n")
        : "• No further pattern gloss available.",
      "The board is a frame of reference — not a verdict. Weigh host and guest, time and circumstance, then decide.",
    ].join("\n\n");
  }
  return [
    `In the ${sys} system the chart is complete. Notice: ${unique.join(", ") || "a quiet board"}.`,
    uniqueGloss[0] ?? "Read the pivotal palaces before concluding.",
    "This supports thought; it does not command. The decision remains yours.",
  ].join("\n\n");
}

export function composeRecommendations(
  patterns: Array<{ name?: string }>,
  locale: Locale,
): string[] {
  if (locale === "vi") {
    return [
      "Đặt câu hỏi rõ: thời điểm, vị thế chủ–khách, điều kiện thắng.",
      patterns.length
        ? "Đối chiếu cách cục với bối cảnh thực — đừng chỉ đọc chữ."
        : "Khi bàn êm, hãy soi kỹ cung chủ sự và giờ hành động.",
      "Giữ biên độ: một phương án dự phòng khi khí xấu xuất hiện.",
    ];
  }
  if (locale === "zh") {
    return [
      "问法宜清：时点、主客、胜负条件。",
      patterns.length
        ? "格局需对照现实情境——不可只读字面。"
        : "盘势平稳时，细察用事宫与行动时辰。",
      "留出余地：气势不利时要有备选方案。",
    ];
  }
  return [
    "State the question cleanly: timing, host–guest stance, win conditions.",
    patterns.length
      ? "Match patterns to real context — do not read words alone."
      : "On a quiet board, study the matter palace and hour of action.",
    "Keep margin: a fallback when the climate turns adverse.",
  ];
}
