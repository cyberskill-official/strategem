/**
 * Chu-khach DecisionFrame presenter types — TASK-STRAT-003.
 * Mirrors packages/tamthuc_strat/chu_khach.py DecisionFrame.
 */

export type Lens = "competitor" | "risk" | "partner";

export type DungThanAssignment = {
  party: "chu" | "khach";
  role_label: string;
  dung_than: string;
  cung: number | null;
};

export type Signal = {
  kind: string;
  reading: string;
  citations: string[];
};

export type DecisionHandoff = {
  prompt: string;
  disclosure: {
    model: string;
    limits: string;
    review_status?: string;
  };
};

export type DecisionFrame = {
  question: string;
  lens: Lens;
  step1_framing: DungThanAssignment[];
  step2_signals: Signal[];
  step3_context_prompts: string[];
  step4_decision: DecisionHandoff;
};

const LENS_LABELS: Record<Lens, [string, string]> = {
  competitor: ["us", "the competitor"],
  risk: ["the action we take", "the external event"],
  partner: ["us", "the partner / hire"],
};

/** Present four decision steps as structured sections (no verdict). */
export function presentDecisionFrame(frame: DecisionFrame): {
  title: string;
  steps: { id: string; heading: string; body: string[] }[];
} {
  const [chu, khach] = LENS_LABELS[frame.lens];
  return {
    title: `Decision frame · ${frame.lens}`,
    steps: [
      {
        id: "step1",
        heading: "1. Framing",
        body: frame.step1_framing.map(
          (a) =>
            `${a.party} (${a.role_label || (a.party === "chu" ? chu : khach)}): ${a.dung_than}` +
            (a.cung != null ? ` @cung ${a.cung}` : ""),
        ),
      },
      {
        id: "step2",
        heading: "2. Signals",
        body: frame.step2_signals.map(
          (s) => `${s.kind}: ${s.reading} [${s.citations.join(", ")}]`,
        ),
      },
      {
        id: "step3",
        heading: "3. Context",
        body: frame.step3_context_prompts,
      },
      {
        id: "step4",
        heading: "4. Decision (you decide)",
        body: [
          frame.step4_decision.prompt,
          `AI · ${frame.step4_decision.disclosure.model}: ${frame.step4_decision.disclosure.limits}`,
        ],
      },
    ],
  };
}
