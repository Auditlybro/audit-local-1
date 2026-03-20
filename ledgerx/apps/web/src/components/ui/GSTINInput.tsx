"use client";

import { useState, useCallback } from "react";

const GSTIN_REGEX = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$/;

export function GSTINInput({
  value,
  onChange,
  placeholder = "22AAAAA0000A1Z5",
  className,
  ...props
}: {
  value: string;
  onChange: (v: string, valid: boolean) => void;
  placeholder?: string;
  className?: string;
} & Omit<React.InputHTMLAttributes<HTMLInputElement>, "value" | "onChange">) {
  const [touched, setTouched] = useState(false);
  const v = value.toUpperCase().replace(/\s/g, "");
  const valid = v.length === 0 || GSTIN_REGEX.test(v);

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const next = e.target.value.toUpperCase().replace(/[^0-9A-Z]/g, "").slice(0, 15);
      onChange(next, next.length === 0 || GSTIN_REGEX.test(next));
    },
    [onChange]
  );

  return (
    <input
      type="text"
      value={value}
      onChange={handleChange}
      onBlur={() => setTouched(true)}
      placeholder={placeholder}
      maxLength={15}
      className={`rounded-lg border bg-navy-400 px-3 py-2 text-white placeholder-slate-500 ${
        touched && !valid ? "border-red-500" : "border-navy-100/30"
      } ${className ?? ""}`}
      {...props}
    />
  );
}
