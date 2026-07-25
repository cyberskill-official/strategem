"use client";

import { useState, type KeyboardEvent, type ReactNode } from "react";
import { Button } from "../ui/button";
import { useLocale } from "../i18n/locale-provider";

export type PromptInputProps = {
  value?: string;
  onChange?: (value: string) => void;
  onSubmit?: (value: string) => void;
  placeholder?: string;
  sendLabel?: string;
  hint?: ReactNode;
  disabled?: boolean;
  busy?: boolean;
  className?: string;
  "data-testid"?: string;
};

/**
 * Prompt box — @cyberskill/design `.cs-prompt` markup contract.
 * Enter submits; Shift+Enter inserts a newline. ≥44px field height.
 *
 * Deliberately local (markup parity with the DS PromptInput in src/ds): the
 * DS component cannot carry data-testid / aria-label on the textarea, does
 * not disable the field while busy or the send button when empty, and its
 * built-in hint strings are vi/en only (app is vi/en/zh). Fold back into
 * src/ds once upstream supports these.
 */
export function PromptInput({
  value,
  onChange,
  onSubmit,
  placeholder,
  sendLabel,
  hint,
  disabled = false,
  busy = false,
  className,
  "data-testid": testId = "follow-up-prompt",
}: PromptInputProps) {
  const { t } = useLocale();
  const [inner, setInner] = useState("");
  const val = value != null ? value : inner;
  const setVal = (v: string) => (onChange ? onChange(v) : setInner(v));

  function submit() {
    if (disabled || busy || !String(val).trim()) return;
    onSubmit?.(val);
  }

  function onKey(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  return (
    <div className={["cs-prompt", className].filter(Boolean).join(" ")} data-testid={testId}>
      <textarea
        className="cs-prompt__field"
        rows={2}
        value={val}
        placeholder={placeholder ?? t("chat.placeholder")}
        disabled={disabled || busy}
        onChange={(e) => setVal(e.target.value)}
        onKeyDown={onKey}
        aria-label={placeholder ?? t("chat.placeholder")}
        data-testid="follow-up-input"
      />
      <div className="cs-prompt__bar">
        {(hint ?? t("chat.hint")) ? (
          <span className="cs-prompt__hint">
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.8"
              strokeLinecap="round"
              strokeLinejoin="round"
              aria-hidden
            >
              <path d="M12 3l1.8 5.4L19 10l-5.2 1.6L12 17l-1.8-5.4L5 10l5.2-1.6z" />
            </svg>
            {hint ?? t("chat.hint")}
          </span>
        ) : null}
        <Button
          type="button"
          size="md"
          disabled={disabled || busy || !String(val).trim()}
          onClick={submit}
          data-testid="follow-up-send"
          aria-busy={busy}
        >
          {busy ? t("chat.busy") : (sendLabel ?? t("chat.send"))}
        </Button>
      </div>
    </div>
  );
}
