/**
 * COV-013 — Four-level curriculum (L1–L4) wired to EDU-001 shape.
 * Beginner tone; classical names secondary. Local persistence of learner level.
 */

export type Locale = "vi" | "en" | "zh";

export type CurriculumLevel = {
  id: "L1" | "L2" | "L3" | "L4";
  order: number;
  name: Record<Locale, string>;
  summary: Record<Locale, string>;
  criteria: { id: string; label: Record<Locale, string> }[];
  unlocks: string[];
  practiceHref: string;
  /** Prior level id required (null for L1) */
  prerequisite: "L1" | "L2" | "L3" | null;
};

export const LEARNER_LEVEL_KEY = "tamthuc.learnerLevel.v1";
export const LEARNER_CRITERIA_KEY = "tamthuc.learnerCriteria.v1";

export const CURRICULUM_LEVELS: CurriculumLevel[] = [
  {
    id: "L1",
    order: 1,
    prerequisite: null,
    name: {
      vi: "Nền tảng",
      en: "Foundations",
      zh: "基础",
    },
    summary: {
      vi: "Nhận ra ban đồ, huy hiệu cát/hung, và câu hỏi rõ trước khi bấm nút.",
      en: "Spot the board, polarity badges, and a clear question before you cast.",
      zh: "先认盘、吉凶标记，并把问题问清楚。",
    },
    criteria: [
      {
        id: "identify_ban_components",
        label: {
          vi: "Chỉ ra được vài thành phần trên ban",
          en: "Point out a few board components",
          zh: "能指出盘上若干要素",
        },
      },
      {
        id: "read_polarity_badge",
        label: {
          vi: "Đọc được huy hiệu cát / hung / trung",
          en: "Read cat / hung / neutral badges",
          zh: "读懂吉 / 凶 / 中标记",
        },
      },
    ],
    unlocks: ["cast_demo"],
    practiceHref: "/cast?system=qimen",
  },
  {
    id: "L2",
    order: 2,
    prerequisite: "L1",
    name: {
      vi: "Một hệ — một lần thử",
      en: "Single-system cast",
      zh: "单系统起盘",
    },
    summary: {
      vi: "Tự thử một hệ (la bàn thời điểm) và nhận ra ít nhất một cách cục.",
      en: "Cast one system (timing compass) and notice at least one pattern.",
      zh: "用时机罗盘起一盘，认出至少一个格局。",
    },
    criteria: [
      {
        id: "cast_qimen",
        label: {
          vi: "Hoàn thành một lần thử Kỳ Môn",
          en: "Complete a QiMen cast",
          zh: "完成一次奇门起盘",
        },
      },
      {
        id: "match_one_cach_cuc",
        label: {
          vi: "Nhận ra một cách cục trên kết quả",
          en: "Match one pattern on results",
          zh: "在结果中认出一个格局",
        },
      },
    ],
    unlocks: ["practice_grader"],
    practiceHref: "/cast?system=qimen",
  },
  {
    id: "L3",
    order: 3,
    prerequisite: "L2",
    name: {
      vi: "Đọc kèm trích dẫn",
      en: "Interpretation with citations",
      zh: "带出处的解读",
    },
    summary: {
      vi: "Mọi gợi ý gắn nguồn; không biến thành lời bói chắc chắn.",
      en: "Hints stay cited; never a sure fortune.",
      zh: "提示都有出处；不是铁口断言。",
    },
    criteria: [
      {
        id: "cite_classical",
        label: {
          vi: "Thấy trích dẫn trên diễn giải",
          en: "See citations on the reading",
          zh: "在解读中看到出处",
        },
      },
      {
        id: "no_verdict_framing",
        label: {
          vi: "Phân biệt gợi ý với lời kết",
          en: "Tell hint from verdict",
          zh: "分清提示与定论",
        },
      },
    ],
    unlocks: ["report_view"],
    practiceHref: "/patterns",
  },
  {
    id: "L4",
    order: 4,
    prerequisite: "L3",
    name: {
      vi: "Đối chiếu nhiều hệ",
      en: "Cross-system comparison",
      zh: "跨系统对照",
    },
    summary: {
      vi: "So hai–ba hệ cùng một thời điểm; hiểu phạm vi khác nhau không phải mâu thuẫn.",
      en: "Compare two–three systems at one moment; different scopes are not contradictions.",
      zh: "同一时刻对照两三个系统；范围不同不等于矛盾。",
    },
    criteria: [
      {
        id: "compare_two_systems",
        label: {
          vi: "Chạy đối chiếu ít nhất hai hệ",
          en: "Run a two-system compare",
          zh: "完成至少两式对照",
        },
      },
      {
        id: "scope_awareness",
        label: {
          vi: "Nói được mỗi hệ nhìn ở tầm nào",
          en: "Name each system’s scope",
          zh: "能说出各系统的观察范围",
        },
      },
    ],
    unlocks: ["cross_system_validate"],
    practiceHref: "/cross-system",
  },
];

export function loadCompletedCriteria(): Set<string> {
  if (typeof window === "undefined") return new Set();
  try {
    const raw = localStorage.getItem(LEARNER_CRITERIA_KEY);
    if (!raw) return new Set();
    const arr = JSON.parse(raw) as string[];
    return new Set(Array.isArray(arr) ? arr : []);
  } catch {
    return new Set();
  }
}

export function saveCompletedCriteria(ids: Set<string>): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(LEARNER_CRITERIA_KEY, JSON.stringify([...ids]));
  } catch {
    /* ignore */
  }
}

export function loadLearnerLevel(): string {
  if (typeof window === "undefined") return "L1";
  try {
    return localStorage.getItem(LEARNER_LEVEL_KEY) || "L1";
  } catch {
    return "L1";
  }
}

export function saveLearnerLevel(id: string): void {
  if (typeof window === "undefined") return;
  try {
    localStorage.setItem(LEARNER_LEVEL_KEY, id);
  } catch {
    /* ignore */
  }
}

/** EDU-001 progression: all prior criteria must be done. */
export function progressionOk(completed: Set<string>, targetLevel: string): boolean {
  const target = CURRICULUM_LEVELS.find((l) => l.id === targetLevel);
  if (!target) return false;
  for (const lv of CURRICULUM_LEVELS) {
    if (lv.order >= target.order) break;
    for (const c of lv.criteria) {
      if (!completed.has(c.id)) return false;
    }
  }
  return true;
}

export function isLevelUnlocked(completed: Set<string>, level: CurriculumLevel): boolean {
  if (!level.prerequisite) return true;
  return progressionOk(completed, level.id);
}
