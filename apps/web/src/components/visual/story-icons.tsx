/** Decorative story icons & scenes — pure SVG, no external assets. */

export function IconQuestion({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="56" height="56" aria-hidden>
      <circle
        cx="32"
        cy="32"
        r="30"
        fill="var(--cs-color-surface-raised)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <path
        d="M24 26c0-6 4-10 10-10s10 4 10 9c0 5-4 7-7 9-2 1-3 2-3 5"
        fill="none"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
      <circle cx="34" cy="46" r="2.2" fill="var(--cs-color-brand-ochre)" />
    </svg>
  );
}

export function IconMap({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="56" height="56" aria-hidden>
      <rect
        x="8"
        y="12"
        width="48"
        height="40"
        rx="6"
        fill="var(--cs-color-surface-raised)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <path
        d="M20 40 L28 22 L36 34 L44 18 L52 40"
        fill="none"
        stroke="var(--cs-color-brand-ochre)"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />
      <circle cx="28" cy="22" r="3" fill="var(--cs-color-brand-umber)" />
    </svg>
  );
}

export function IconStep({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="56" height="56" aria-hidden>
      <circle cx="32" cy="32" r="30" fill="var(--cs-color-brand-umber)" />
      <path
        d="M22 34 L30 42 L44 24"
        fill="none"
        stroke="var(--cs-color-brand-ochre)"
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function IconCompass({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="48" height="48" aria-hidden>
      <circle
        cx="32"
        cy="32"
        r="28"
        fill="var(--cs-color-surface-panel)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <path d="M32 12 L36 32 L32 52 L28 32 Z" fill="var(--cs-color-brand-ochre)" opacity="0.9" />
      <path d="M12 32 L32 28 L52 32 L32 36 Z" fill="var(--cs-color-brand-umber)" opacity="0.35" />
      <circle cx="32" cy="32" r="4" fill="var(--cs-color-brand-umber)" />
    </svg>
  );
}

export function IconDialogue({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="48" height="48" aria-hidden>
      <rect
        x="8"
        y="10"
        width="34"
        height="24"
        rx="8"
        fill="var(--cs-color-surface-raised)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <rect x="22" y="30" width="34" height="24" rx="8" fill="var(--cs-color-brand-ochre)" opacity="0.85" />
      <circle cx="20" cy="22" r="2" fill="var(--cs-color-brand-umber)" />
      <circle cx="28" cy="22" r="2" fill="var(--cs-color-brand-umber)" />
      <circle cx="36" cy="22" r="2" fill="var(--cs-color-brand-umber)" />
    </svg>
  );
}

export function IconSeasons({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="48" height="48" aria-hidden>
      <circle
        cx="32"
        cy="32"
        r="28"
        fill="var(--cs-color-surface-raised)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <path d="M32 8 A24 24 0 0 1 56 32 L32 32 Z" fill="var(--cs-color-brand-ochre)" opacity="0.7" />
      <path d="M56 32 A24 24 0 0 1 32 56 L32 32 Z" fill="var(--cs-color-brand-umber)" opacity="0.25" />
      <path d="M32 56 A24 24 0 0 1 8 32 L32 32 Z" fill="var(--cs-color-brand-umber)" opacity="0.45" />
      <circle
        cx="32"
        cy="32"
        r="6"
        fill="var(--cs-color-surface-panel)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
    </svg>
  );
}

/** Wide hero illustration: person with a question → path → map → open door. */
export function HeroScene({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 480 160"
      width="100%"
      height="auto"
      role="img"
      aria-hidden
    >
      <defs>
        <linearGradient id="heroSky" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor="rgb(244 186 23 / 0.25)" />
          <stop offset="100%" stopColor="rgb(69 33 14 / 0.08)" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="480" height="160" rx="20" fill="url(#heroSky)" />
      {/* Path */}
      <path
        d="M48 110 C 120 90, 180 130, 240 100 S 360 70, 420 95"
        fill="none"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2.5"
        strokeDasharray="6 6"
        opacity="0.45"
      />
      {/* Figure with question */}
      <circle cx="56" cy="88" r="18" fill="var(--cs-color-surface-panel)" stroke="var(--cs-color-brand-umber)" strokeWidth="2" />
      <circle cx="56" cy="82" r="6" fill="var(--cs-color-brand-umber)" />
      <path d="M46 98 Q56 108 66 98" fill="none" stroke="var(--cs-color-brand-umber)" strokeWidth="2" />
      <circle cx="78" cy="58" r="14" fill="var(--cs-color-brand-ochre)" />
      <text x="78" y="63" textAnchor="middle" fontSize="16" fontWeight="700" fill="var(--cs-color-brand-umber)">
        ?
      </text>
      {/* Map board */}
      <rect
        x="190"
        y="48"
        width="100"
        height="72"
        rx="10"
        fill="var(--cs-color-surface-panel)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <line x1="223" y1="48" x2="223" y2="120" stroke="var(--cs-color-border-default)" strokeWidth="1.5" />
      <line x1="257" y1="48" x2="257" y2="120" stroke="var(--cs-color-border-default)" strokeWidth="1.5" />
      <line x1="190" y1="72" x2="290" y2="72" stroke="var(--cs-color-border-default)" strokeWidth="1.5" />
      <line x1="190" y1="96" x2="290" y2="96" stroke="var(--cs-color-border-default)" strokeWidth="1.5" />
      <circle cx="240" cy="84" r="8" fill="var(--cs-color-brand-ochre)" opacity="0.9" />
      {/* Open door / decision */}
      <rect
        x="380"
        y="42"
        width="52"
        height="88"
        rx="6"
        fill="var(--cs-color-brand-umber)"
      />
      <path d="M406 42 L432 52 L432 120 L406 130 Z" fill="var(--cs-color-brand-ochre)" opacity="0.85" />
      <circle cx="424" cy="86" r="3" fill="var(--cs-color-brand-umber)" />
    </svg>
  );
}

export function IconBook({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 64 64" width="48" height="48" aria-hidden>
      <path
        d="M12 14 h18 a6 6 0 0 1 6 6 v30 a6 6 0 0 0 -6 -6 H12 Z"
        fill="var(--cs-color-surface-raised)"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
      <path
        d="M52 14 H34 a6 6 0 0 0 -6 6 v30 a6 6 0 0 1 6 -6 h18 Z"
        fill="var(--cs-color-brand-ochre)"
        opacity="0.75"
        stroke="var(--cs-color-brand-umber)"
        strokeWidth="2"
      />
    </svg>
  );
}
