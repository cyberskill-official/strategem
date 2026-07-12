"use client";

import { useEffect, useState } from "react";
import {
  isPinned,
  togglePin,
  type SavedChart,
} from "../../lib/pins/saved-charts";
import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

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
  const [pinned, setPinned] = useState(false);

  useEffect(() => {
    setPinned(isPinned(queryId));
  }, [queryId]);

  return (
    <Button
      type="button"
      variant={pinned ? "accent" : "secondary"}
      data-testid="pin-chart-button"
      aria-pressed={pinned}
      onClick={() => {
        const chart: Omit<SavedChart, "pinned_at"> = {
          query_id: queryId,
          he,
          question_type: questionType,
          cast_at: castAt ?? new Date().toISOString(),
          report_id: reportId,
        };
        const res = togglePin(chart);
        setPinned(res.pinned);
      }}
      style={{ minHeight: 40 }}
    >
      {pinned ? t("results.unpin") : t("results.pin")}
    </Button>
  );
}
