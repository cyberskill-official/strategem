"use client";

export function ShareDialog({
  url,
  onClose,
}: {
  url: string;
  onClose: () => void;
}) {
  return (
    <div
      role="dialog"
      data-testid="share-dialog"
      style={{
        border: "1px solid var(--color-border)",
        padding: 12,
        borderRadius: 8,
      }}
    >
      <p>Share link</p>
      <code data-testid="share-url">{url}</code>
      <button type="button" onClick={onClose}>
        Close
      </button>
    </div>
  );
}
