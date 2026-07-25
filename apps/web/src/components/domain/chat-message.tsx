"use client";

import type { ReactNode } from "react";
import { useLocale } from "../i18n/locale-provider";

export type ChatRole = "lumi" | "user";

export type ChatMessageProps = {
  role?: ChatRole;
  name?: ReactNode;
  avatar?: ReactNode;
  children?: ReactNode;
  className?: string;
  "data-testid"?: string;
};

/**
 * Chat turn — @cyberskill/design `.cs-chat-msg` markup contract.
 * role "lumi" (assistant, left) or "user" (right).
 *
 * Deliberately local (markup parity with the DS ChatMessage in src/ds): the
 * DS component does not spread rest props, so it cannot carry the
 * data-testid / role="listitem" hooks e2e relies on, and its default names
 * are not zh-localizable. Fold back into src/ds once upstream spreads props.
 */
export function ChatMessage({
  role = "lumi",
  name,
  avatar,
  children,
  className,
  "data-testid": testId,
}: ChatMessageProps) {
  const { t } = useLocale();
  const isUser = role === "user";
  const defaultAvatar = isUser ? (
    <span aria-hidden>Bạn</span>
  ) : (
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden
    >
      <path d="M12 3l1.8 5.4L19 10l-5.2 1.6L12 17l-1.8-5.4L5 10l5.2-1.6z" />
    </svg>
  );

  return (
    <div
      className={[
        "cs-chat-msg",
        isUser ? "cs-chat-msg--user" : "cs-chat-msg--lumi",
        className,
      ]
        .filter(Boolean)
        .join(" ")}
      data-testid={testId ?? (isUser ? "chat-msg-user" : "chat-msg-assistant")}
      role="listitem"
    >
      <div className="cs-chat-msg__avatar">{avatar ?? defaultAvatar}</div>
      <div className="cs-chat-msg__col">
        <div className="cs-chat-msg__name">
          {name ?? (isUser ? t("chat.you") : t("chat.assistant"))}
        </div>
        <div className="cs-chat-msg__bubble">{children}</div>
      </div>
    </div>
  );
}
