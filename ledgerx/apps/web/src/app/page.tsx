"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function HomePage() {
  const router = useRouter();

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
    // Attempt soft navigation first
    if (token) router.replace("/dashboard");
    else router.replace("/login");
    
    // Fallback force navigation if Next.js client router hangs (e.g., missing chunks or Suspense locks)
    const fallback = setTimeout(() => {
       window.location.assign(token ? "/dashboard" : "/login");
    }, 1000);
    
    return () => clearTimeout(fallback);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-navy-500">
      <div className="flex flex-col items-center gap-3">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-gold border-t-transparent" aria-hidden />
        <p className="text-slate-400">Taking you to sign in…</p>
      </div>
    </div>
  );
}
