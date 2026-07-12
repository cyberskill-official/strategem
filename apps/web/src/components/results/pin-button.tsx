"use client";

import { useCallback, useSyncExternalStore } from "react";
import {
  isPinned,
  togglePin,
  type SavedChart,
} from "../../lib/pins/saved-charts";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

const PIN_EVENT = "tamthuc:pins-changed";

function subscribePins(onChange: () => void) {
  if (typeof window === "undefined") return () => {};
  const handler = () => onChange();
  window.addEventListener(PIN_EVENT, handler);
  window.addEventListener("storage", handler);
  return () => {
    window.removeEventListener(PIN_EVENT, handler);
    window.removeEventListener("storage", handler);
  };
}

function notifyPinsChanged() {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(PIN_EVENT));
  }
}

export function PinButton({
  queryId,
  he,
  questionType,
  castAt,
  reportId,
}: {
  queryId: string;
  he: string;
  questionType: string;
  castAt?: string;
  reportId?: string;
}) {
  const { t } = useLocale();
  const pinned = useSyncExternalStore(
    subscribePins,
    () => isPinned(queryId),
    () => false,
  );

  const onToggle = useCallback(() => {
    const chart: Omit<SavedChart, "pinned_at"> = {
      query_id: queryId,
      he,
      question_type: questionType,
      cast_at: castAt ?? new Date().toISOString(),
      report_id: reportId,
    };
    togglePin(chart);
    notifyPinsChanged();
  }, [queryId, he, questionType, castAt, reportId]);

  return (
    <Button
      type="button"
      variant={pinned ? "accent" : "secondary"}
      data-testid="pin-chart-button"
      aria-pressed={pinned}
      onClick={onToggle}
      style={{ minHeight: 40 }}
    >
      {pinned ? t("results.unpin") : t("results.pin")}
    </Button>
  );
}
