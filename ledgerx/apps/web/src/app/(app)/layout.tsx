"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAppStore, useNavStore } from "@/lib/store";
import { Sidebar } from "@/components/ui/Sidebar";
import { TopBar } from "@/components/ui/TopBar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const user = useAppStore((s) => s.user);
  const isNavigating = useNavStore((s) => s.isNavigating);

  useEffect(() => {
    const token =
      typeof window !== "undefined"
        ? localStorage.getItem("access_token")
        : null;
    if (
      !token &&
      !pathname?.startsWith("/login") &&
      !pathname?.startsWith("/register")
    ) {
      router.replace("/login");
    }
  }, [pathname, router]);

  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-navy">
        <div className="text-slate-400">Loading…</div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-navy">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 relative">
          {isNavigating && (
            <div className="absolute inset-0 bg-navy/50 z-50 flex items-center justify-center backdrop-blur-sm">
              <div className="flex flex-col items-center gap-3">
                <div
                  className="h-8 w-8 animate-spin rounded-full border-2 border-gold border-t-transparent"
                  aria-hidden
                />
                <p className="text-slate-400">Loading…</p>
              </div>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}
