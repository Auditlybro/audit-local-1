"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function AuthError({
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
    <div className="min-h-screen flex items-center justify-center bg-navy-500 p-6">
      <div className="rounded-2xl border border-navy-100/20 bg-navy-400/80 p-8 shadow-xl max-w-md w-full text-center">
        <h2 className="text-xl font-bold text-gold">Sign-in error</h2>
        <p className="mt-2 text-sm text-slate-400">
          {error?.message || "Something went wrong. Check the backend is running (port 8001)."}
        </p>
        <div className="mt-6 flex flex-col gap-2">
          <button
            type="button"
            onClick={() => reset()}
            className="w-full rounded-lg bg-gold py-2.5 font-medium text-navy hover:bg-gold-light"
          >
            Try again
          </button>
          <Link
            href="/login"
            className="block w-full rounded-lg border border-navy-100/30 py-2.5 text-sm text-slate-300 hover:bg-navy-300"
          >
            Back to login
          </Link>
        </div>
      </div>
    </div>
  );
}
