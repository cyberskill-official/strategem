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

/**
 * Short story summary for results header (WEB-019).
 * Beginner-safe: metaphors + soft stance, never destiny claims.
 */
export function composeStorySummary(
  input: ReadingInput,
  locale: Locale,
): { lines: string[]; stance: "cat" | "hung" | "trung" | null } {
  const he = (input.he ?? "").toLowerCase();
  const systemKey =
    he === "qimen" || he === "ky_mon"
      ? "qimen"
      : he === "liuren" || he === "luc_nham"
        ? "liuren"
        : he === "taiyi" || he === "thai_at"
          ? "taiyi"
          : he || "qimen";

  // Unique patterns by display name (API may emit same pattern on multiple palaces)
  const seenNames = new Set<string>();
  const top: ReadingInput["patterns"] = [];
  for (const p of input.patterns) {
    const key = (p.name ?? "").trim();
    if (!key || seenNames.has(key)) continue;
    seenNames.add(key);
    top.push(p);
    if (top.length >= 3) break;
  }
  let stance: "cat" | "hung" | "trung" | null = null;
  for (const p of top) {
    const pol = (p.polarity ?? "").toLowerCase();
    if (pol === "hung" || pol === "inauspicious") {
      stance = "hung";
      break;
    }
    if (pol === "cat" || pol === "auspicious") stance = stance ?? "cat";
    if (pol === "trung" || pol === "neutral") stance = stance ?? "trung";
  }
  if (!stance && top.length) stance = "trung";

  const lines: string[] = [];

  // System metaphor line
  if (locale === "vi") {
    const sysLine: Record<string, string> = {
      qimen: "Bạn đang nhìn qua la bàn thời điểm.",
      liuren: "Bạn đang nhìn cuộc trò chuyện giữa hai phía.",
      taiyi: "Bạn đang nhìn nhịp lớn của một chặng đường.",
    };
    lines.push(sysLine[systemKey] ?? sysLine.qimen);
  } else if (locale === "zh") {
    const sysLine: Record<string, string> = {
      qimen: "你正透过时机的罗盘来看。",
      liuren: "你正看双方之间的一场对话。",
      taiyi: "你正看一段路的大节奏。",
    };
    lines.push(sysLine[systemKey] ?? sysLine.qimen);
  } else {
    const sysLine: Record<string, string> = {
      qimen: "You are looking through a timing compass.",
      liuren: "You are looking at a conversation between two sides.",
      taiyi: "You are looking at the long rhythm of a chapter.",
    };
    lines.push(sysLine[systemKey] ?? sysLine.qimen);
  }

  if (!top.length) {
    if (locale === "vi") {
      lines.push(
        "Bàn đã vẽ xong. Chưa có điểm nổi bật — hãy nhìn hình và đặt câu hỏi cụ thể hơn nếu cần.",
      );
    } else if (locale === "zh") {
      lines.push("图已画成。暂无突出亮点——先看图，或把问题问得更具体。");
    } else {
      lines.push(
        "The picture is drawn. Nothing stands out yet — look at the board, or sharpen the question.",
      );
    }
  } else {
    for (const p of top.slice(0, 2)) {
      const name = displayPatternName(p.name ?? "", locale);
      const gloss = patternGloss(p.name ?? "", locale);
      if (locale === "vi") {
        lines.push(gloss ? `Điểm nổi: ${name}. ${gloss}` : `Điểm nổi: ${name}.`);
      } else if (locale === "zh") {
        lines.push(gloss ? `亮点：${name}。${gloss}` : `亮点：${name}。`);
      } else {
        lines.push(gloss ? `Standing out: ${name}. ${gloss}` : `Standing out: ${name}.`);
      }
    }
    if (stance === "hung") {
      lines.push(
        locale === "vi"
          ? "Gợi ý nhẹ: nên chậm lại, kiểm tra điều kiện trước khi tiến."
          : locale === "zh"
            ? "轻提示：宜放慢，先核对条件再前进。"
            : "Soft hint: slow down; check conditions before advancing.",
      );
    } else if (stance === "cat") {
      lines.push(
        locale === "vi"
          ? "Gợi ý nhẹ: có thể mở thêm một bước — vẫn giữ biên độ."
          : locale === "zh"
            ? "轻提示：可再迈一步——仍留余地。"
            : "Soft hint: you may open a step — keep a margin.",
      );
    } else if (stance === "trung") {
      lines.push(
        locale === "vi"
          ? "Gợi ý nhẹ: bàn đang trung tính — hãy soi thêm bối cảnh thực."
          : locale === "zh"
            ? "轻提示：盘势中性——对照现实情境。"
            : "Soft hint: the board is neutral — weigh real context.",
      );
    }
  }

  lines.push(
    locale === "vi"
      ? "Đây là khung để nghĩ, không phải lời phán. Quyết định vẫn là của bạn."
      : locale === "zh"
        ? "这是思考框架，不是裁决。决定权仍在你。"
        : "This is a thinking frame, not a verdict. The decision stays yours.",
  );

  return { lines, stance };
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
