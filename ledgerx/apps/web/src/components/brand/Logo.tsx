"use client";

import clsx from "clsx";

const GOLD = "#C9A84C";
const NAVY = "#0B1120";

type LogoProps = {
  className?: string;
  /** Full = mark + wordmark; mark = icon only (e.g. collapsed sidebar) */
  variant?: "full" | "mark";
  /** Visual size of the mark */
  size?: "sm" | "md" | "lg";
};

const markPx = { sm: 28, md: 36, lg: 44 };

/**
 * LedgerX brand: navy rounded tile with gold “LX” monogram (ledger + cross-check).
 */
export function Logo({ className, variant = "full", size = "md" }: LogoProps) {
  const px = markPx[size];
  const textClass =
    size === "sm"
      ? "text-base"
      : size === "lg"
        ? "text-2xl"
        : "text-xl";

  return (
    <div className={clsx("flex items-center gap-2.5", className)}>
      <svg
        width={px}
        height={px}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0"
        aria-hidden
        role="img"
      >
        <rect
          x="1"
          y="1"
          width="38"
          height="38"
          rx="9"
          fill={NAVY}
          stroke={GOLD}
          strokeWidth="1.5"
        />
        <path
          fill={GOLD}
          d="M8 8h4v18H8V8zm0 18h12v4H8v-4z"
        />
        <path
          stroke={GOLD}
          strokeWidth="2.2"
          strokeLinecap="round"
          d="M24 10l8 20M32 10l-8 20"
        />
      </svg>
      {variant === "full" && (
        <span
          className={clsx(
            "font-semibold tracking-tight text-gold select-none",
            textClass
          )}
        >
          Ledger<span className="text-gold-light">X</span>
        </span>
      )}
    </div>
  );
}
