"use client";

import { useEffect } from "react";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-navy-500 p-6">
      <div className="rounded-2xl border border-navy-100/20 bg-navy-400/80 p-8 shadow-xl max-w-md w-full text-center">
        <h2 className="text-xl font-bold text-gold">Something went wrong</h2>
        <p className="mt-2 text-sm text-slate-400">
          {error?.message || "An error occurred."}
        </p>
        <button
          type="button"
          onClick={() => reset()}
          className="mt-6 w-full rounded-lg bg-gold py-2.5 font-medium text-navy hover:bg-gold-light"
        >
          Try again
        </button>
      </div>
    </div>
  );
}
