"use client";

import { useLocale } from "../i18n/locale-provider";

const SEGMENTS = 5;

type Tone = "low" | "medium" | "high";

const TONE_COLOR: Record<Tone, string> = {
  low: "var(--cs-color-semantic-danger)",
  medium: "var(--cs-color-semantic-warning)",
  high: "var(--cs-color-semantic-success)",
};

/**
 * Segmented AI-confidence indicator — @cyberskill/design `.cs-confidence`
 * markup contract. Confidence is always stated in words too, never colour
 * alone (pairs with AIDisclosureBadge / HumanReviewGate).
 *
 * Deliberately local (markup parity with the DS ConfidenceMeter in src/ds):
 * the DS level words (Low/Medium/High) come from its built-in vi/en strings
 * with no override prop, which would regress the zh locale. Fold back into
 * src/ds once upstream allows level-text overrides.
 */
export function ConfidenceMeter({ value }: { value: number }) {
  const { t } = useLocale();
  const clamped = Math.min(1, Math.max(0, value));
  const tone: Tone = clamped < 0.4 ? "low" : clamped < 0.75 ? "medium" : "high";
  const filled = Math.max(1, Math.round(clamped * SEGMENTS));
  const label = t("confidence.label");
  const levelText = t(`confidence.${tone}`);
  return (
    <div className="cs-confidence" data-testid="confidence-meter">
      <div className="cs-confidence__head">
        <span>{label}</span>
        <span className="cs-confidence__level" style={{ color: TONE_COLOR[tone] }}>
          {levelText}
        </span>
      </div>
      <div
        className="cs-confidence__track"
        role="meter"
        aria-valuemin={0}
        aria-valuemax={SEGMENTS}
        aria-valuenow={filled}
        aria-label={`${label}: ${levelText}`}
      >
        {Array.from({ length: SEGMENTS }).map((_, i) => (
          <span
            key={i}
            className="cs-confidence__seg"
            style={i < filled ? { background: TONE_COLOR[tone] } : undefined}
          />
        ))}
      </div>
    </div>
  );
}
