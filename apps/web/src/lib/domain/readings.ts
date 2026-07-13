/**
 * Locale-native literary readings for UI when API returns English stubs.
 * Does NOT machine-translate classical text; composes expert-authored templates.
 * Beginner-safe: no destiny guarantees.
 */

import type { Locale } from "../../i18n/routing";
import { displayPatternName, patternGloss } from "./glossary";

export type ReadingInput = {
  he?: string;
  patterns: Array<{
    name?: string;
    polarity?: string;
    cung?: number | null;
    score?: number | null;
  }>;
  persona: "beginner" | "expert";
};

const SYSTEM: Record<string, Record<Locale, string>> = {
  ky_mon: { vi: "Kỳ Môn", en: "Qi Men", zh: "奇门" },
  luc_nham: { vi: "Lục Nhâm", en: "Liu Ren", zh: "六壬" },
  thai_at: { vi: "Thái Ất", en: "Tai Yi", zh: "太乙" },
  qimen: { vi: "Kỳ Môn", en: "Qi Men", zh: "奇门" },
  liuren: { vi: "Lục Nhâm", en: "Liu Ren", zh: "六壬" },
  taiyi: { vi: "Thái Ất", en: "Tai Yi", zh: "太乙" },
};

function systemName(he: string | undefined, locale: Locale): string {
  if (!he) return SYSTEM.ky_mon[locale];
  return SYSTEM[he]?.[locale] ?? he;
}

function isEnglishStub(text: string | undefined | null): boolean {
  if (!text) return true;
  if (/Educational reading for|Technical notes for|Detected patterns:/.test(text))
    return true;
  const letters = text.replace(/[^A-Za-zÀ-ỹ]/g, "");
  if (letters.length < 20) return false;
  const viMarks = (
    text.match(
      /[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ]/gi,
    ) || []
  ).length;
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
  return isEnglishStub(text);
}

/** Sort by score desc, unique by name, hung preferred for stance. */
export function rankPatterns(
  patterns: ReadingInput["patterns"],
): ReadingInput["patterns"] {
  const scored = [...patterns].sort((a, b) => {
    const sa = typeof a.score === "number" ? a.score : 0;
    const sb = typeof b.score === "number" ? b.score : 0;
    if (sb !== sa) return sb - sa;
    const pa = (a.polarity ?? "").toLowerCase();
    const pb = (b.polarity ?? "").toLowerCase();
    const weight = (p: string) => (p === "hung" ? 2 : p === "cat" ? 1 : 0);
    return weight(pb) - weight(pa);
  });
  const seen = new Set<string>();
  const out: ReadingInput["patterns"] = [];
  for (const p of scored) {
    const key = (p.name ?? "").trim();
    if (!key || seen.has(key)) continue;
    seen.add(key);
    out.push(p);
  }
  return out;
}

export function composeReading(input: ReadingInput, locale: Locale): string {
  const sys = systemName(input.he, locale);
  const ranked = rankPatterns(input.patterns);
  const names = ranked
    .map((p) => displayPatternName(p.name ?? "", locale))
    .filter(Boolean);
  const unique = [...new Set(names)];
  const glosses = ranked
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
        "Đọc bàn là khung tham chiếu — không thay cho phán đoán của người hỏi.",
      ].join("\n\n");
    }
    return [
      `Theo ${sys}, bức hình đã thành. Những điểm đáng chú ý: ${unique.join(", ") || "bàn êm, ít điểm nổi"}.`,
      uniqueGloss[0] ? uniqueGloss[0] : "Hãy nhìn các vị trí then chốt trước khi kết luận.",
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
        "读盘为参照框架，不能替代问事者的判断。",
      ].join("\n\n");
    }
    return [
      `依${sys}，图已成。宜留意：${unique.join("、") || "盘势平稳"}。`,
      uniqueGloss[0] ?? "请先读关键位置再下结论。",
      "此为思考辅助，非裁决。决定权在你。",
    ].join("\n\n");
  }

  if (input.persona === "expert") {
    return [
      `${sys} board is fixed. Observed patterns: ${unique.join(" · ") || "none prominent"}.`,
      uniqueGloss.length
        ? uniqueGloss.map((g) => `• ${g}`).join("\n")
        : "• No further pattern gloss available.",
      "The board is a frame of reference — not a verdict.",
    ].join("\n\n");
  }
  return [
    `In the ${sys} system the picture is complete. Notice: ${unique.join(", ") || "a quiet board"}.`,
    uniqueGloss[0] ?? "Read the pivotal places before concluding.",
    "This supports thought; it does not command. The decision remains yours.",
  ].join("\n\n");
}

/**
 * Short story summary — max ~4 lines: system + one best pattern + stance + close.
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

  const top = rankPatterns(input.patterns);
  const best = top[0];
  let stance: "cat" | "hung" | "trung" | null = null;
  if (best) {
    const pol = (best.polarity ?? "").toLowerCase();
    if (pol === "hung" || pol === "inauspicious") stance = "hung";
    else if (pol === "cat" || pol === "auspicious") stance = "cat";
    else stance = "trung";
  }

  const lines: string[] = [];

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

  // COV-006: TaiYi empty-state uses dedicated long-rhythm copy (not silent)
  if (!best) {
    if (systemKey === "taiyi") {
      if (locale === "vi") {
        lines.push(
          "Chưa có cách cục nổi — vẫn xem chủ–khách toán và trường/đoản trên ban Thái Ất.",
        );
      } else if (locale === "zh") {
        lines.push("暂无突出格局——仍可看太乙主客算与长短计数。");
      } else {
        lines.push(
          "No standing pattern yet — still read host/guest counts and long/short on the TaiYi board.",
        );
      }
    } else if (locale === "vi") {
      lines.push(
        "Hình đã vẽ xong. Chưa có điểm nổi bật — hãy nhìn hình, hoặc hỏi cụ thể hơn.",
      );
    } else if (locale === "zh") {
      lines.push("图已画成。暂无突出亮点——先看图，或把问题问得更具体。");
    } else {
      lines.push(
        "The picture is drawn. Nothing stands out yet — look first, or sharpen the question.",
      );
    }
  } else {
    const name = displayPatternName(best.name ?? "", locale);
    const gloss = patternGloss(best.name ?? "", locale);
    if (locale === "vi") {
      lines.push(gloss ? `Điểm nổi: ${name}. ${gloss}` : `Điểm nổi: ${name}.`);
    } else if (locale === "zh") {
      lines.push(gloss ? `亮点：${name}。${gloss}` : `亮点：${name}。`);
    } else {
      lines.push(gloss ? `Standing out: ${name}. ${gloss}` : `Standing out: ${name}.`);
    }
    if (stance === "hung") {
      lines.push(
        locale === "vi"
          ? `Gợi ý nhẹ: nên chậm lại — ${gloss ? "vì điểm trên gợi khí bị chặn." : "kiểm tra điều kiện trước khi tiến."}`
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
    } else {
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
      "Đặt câu hỏi rõ: thời điểm, vị thế hai phía, điều kiện «đủ tốt».",
      patterns.length
        ? "Đối chiếu điểm nổi với bối cảnh thực — đừng chỉ đọc chữ."
        : "Khi hình êm, hãy soi kỹ thời điểm và đối phương.",
      "Giữ biên độ: một phương án dự phòng khi khí xấu xuất hiện.",
    ];
  }
  if (locale === "zh") {
    return [
      "问法宜清：时点、双方、何谓足够好。",
      patterns.length
        ? "亮点需对照现实——不可只读字面。"
        : "盘势平稳时，细察时点与对方。",
      "留出余地：气势不利时要有备选。",
    ];
  }
  return [
    "State the question cleanly: timing, both sides, what “good enough” means.",
    patterns.length
      ? "Match highlights to real context — do not read words alone."
      : "On a quiet board, study timing and the other side.",
    "Keep margin: a fallback when the climate turns adverse.",
  ];
}
