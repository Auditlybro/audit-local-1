"use client";

import { formatINR } from "@/lib/format";
import { cn } from "@/lib/cn";

export function AmountDisplay({
  amount,
  className,
  showZero = true,
}: {
  amount: number | string | null | undefined;
  className?: string;
  showZero?: boolean;
}) {
  const n = amount == null ? 0 : typeof amount === "string" ? parseFloat(amount) : amount;
  if (!showZero && n === 0) return <span className={cn("font-number", className)}>—</span>;
  return <span className={cn("font-number", className)}>{formatINR(n)}</span>;
}
