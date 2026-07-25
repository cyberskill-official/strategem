"use client";

import { useId, useState } from "react";
import { followUp, ApiClientError, type FollowUpResponse } from "../../lib/api/client";
import { useLocale } from "../i18n/locale-provider";
import { AIDisclosureBadge } from "./ai-disclosure-badge";
import { ChatMessage } from "./chat-message";
import { PromptInput } from "./prompt-input";

type Turn = {
  id: string;
  role: "user" | "lumi";
  text: string;
  citations?: string[];
  disclosure?: FollowUpResponse["ai_disclosure"];
  refused?: boolean;
};

/**
 * Follow-up chat on results/report — VI-first, cited, anti-destiny framed.
 * Wires to POST /api/v1/queries/{id}/follow-up.
 */
export function FollowUpChat({ queryId }: { queryId: string }) {
  const { t, locale } = useLocale();
  const listId = useId();
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [turns, setTurns] = useState<Turn[]>([
    {
      id: "seed",
      role: "lumi",
      text: t("chat.welcome"),
    },
  ]);

  async function onSubmit(value: string) {
    const msg = value.trim();
    if (!msg || busy || !queryId) return;
    setBusy(true);
    setError(null);
    setDraft("");
    const userTurn: Turn = { id: `u-${Date.now()}`, role: "user", text: msg };
    setTurns((prev) => [...prev, userTurn]);
    try {
      const res = await followUp(queryId, msg, { locale });
      const answer = res.answer?.beginner || res.answer?.expert || t("chat.error");
      const cites = (res.ai_disclosure?.retrieved_citation_ids ?? []).map(String);
      setTurns((prev) => [
        ...prev,
        {
          id: `a-${Date.now()}`,
          role: "lumi",
          text: answer,
          citations: cites,
          disclosure: res.ai_disclosure,
          refused: res.refused,
        },
      ]);
    } catch (e) {
      if (e instanceof ApiClientError) {
        if (e.code === "NOT_FOUND") setError(t("chat.missingCast"));
        else if (e.code === "NETWORK" || e.status === 0) setError(t("error.apiDown"));
        else setError(e.message || t("chat.error"));
      } else {
        setError(t("chat.error"));
      }
    } finally {
      setBusy(false);
    }
  }

  return (
    <section
      className="cs-follow-up"
      data-testid="follow-up-chat"
      aria-labelledby={`${listId}-title`}
    >
      <header className="cs-follow-up__head">
        <h2 id={`${listId}-title`} className="cs-subhead" style={{ margin: 0 }}>
          {t("chat.title")}
        </h2>
        <p className="cs-muted" style={{ margin: 0 }}>
          {t("chat.subtitle")}
        </p>
      </header>

      <div
        className="cs-chat"
        role="list"
        aria-live="polite"
        aria-relevant="additions"
        data-testid="follow-up-thread"
      >
        {turns.map((turn) => (
          <ChatMessage key={turn.id} role={turn.role}>
            <div className="cs-prose" style={{ whiteSpace: "pre-wrap" }}>
              {turn.text}
            </div>
            {turn.disclosure ? (
              <div style={{ marginTop: 8 }}>
                <AIDisclosureBadge
                  model={turn.disclosure.model ?? "follow-up"}
                  limits={turn.disclosure.limits || t("disclosure.limitsDefault")}
                  citations={turn.citations ?? []}
                  reviewStatus={turn.disclosure.review_status ?? "not_required"}
                />
              </div>
            ) : null}
            {turn.refused ? (
              <p className="cs-muted" style={{ marginTop: 6, marginBottom: 0 }}>
                {t("chat.refusedHint")}
              </p>
            ) : null}
          </ChatMessage>
        ))}
        {busy ? (
          <div className="cs-typing" data-testid="follow-up-typing" aria-label={t("chat.busy")}>
            <span />
            <span />
            <span />
          </div>
        ) : null}
      </div>

      {error ? (
        <p role="alert" className="cs-error-banner" data-testid="follow-up-error">
          {error}
        </p>
      ) : null}

      <PromptInput
        value={draft}
        onChange={setDraft}
        onSubmit={(v) => void onSubmit(v)}
        busy={busy}
        disabled={!queryId}
      />
    </section>
  );
}
