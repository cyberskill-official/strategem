"use client";

import { useLocale } from "../i18n/locale-provider";
import { Button } from "../ui/button";

export function ShareDialog({
  url,
  onClose,
}: {
  url: string;
  onClose: () => void;
}) {
  const { t } = useLocale();
  return (
    <div
      role="dialog"
      data-testid="share-dialog"
      className="cs-card"
      style={{ marginTop: 12 }}
    >
      <p>{t("share.title")}</p>
      <code data-testid="share-url">{url}</code>
      <div style={{ marginTop: 8 }}>
        <Button type="button" variant="secondary" onClick={onClose}>
          {t("share.close")}
        </Button>
      </div>
    </div>
  );
}
