"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAppStore, useNavStore } from "@/lib/store";
import { authApi } from "@/lib/api";
import { Sidebar } from "@/components/ui/Sidebar";
import { TopBar } from "@/components/ui/TopBar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const user = useAppStore((s) => s.user);
  const setUser = useAppStore((s) => s.setUser);
  const isNavigating = useNavStore((s) => s.isNavigating);
  const [authState, setAuthState] = useState<"loading" | "authenticated" | "unauthenticated">("loading");

  useEffect(() => {
    // Wait for Zustand persist to hydrate from localStorage
    const unsub = useAppStore.persist.onFinishHydration(() => {
      const hydratedUser = useAppStore.getState().user;
      const token = localStorage.getItem("access_token");

      if (hydratedUser) {
        setAuthState("authenticated");
      } else if (token) {
        // Token exists but user wasn't persisted — rehydrate from API
        authApi
          .me()
          .then(({ data: me }) => {
            setUser({
              id: me.id,
              email: me.email,
              name: me.name,
              role: me.role,
              org_id: me.org_id,
            });
            setAuthState("authenticated");
          })
          .catch(() => {
            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
            router.replace("/login");
          });
      } else {
        router.replace("/login");
      }
    });

    // Also check immediately in case hydration already finished
    const token = localStorage.getItem("access_token");
    const currentUser = useAppStore.getState().user;
    if (currentUser) {
      setAuthState("authenticated");
    } else if (!token) {
      router.replace("/login");
    } else {
      // Token exists, try to rehydrate
      authApi
        .me()
        .then(({ data: me }) => {
          setUser({
            id: me.id,
            email: me.email,
            name: me.name,
            role: me.role,
            org_id: me.org_id,
          });
          setAuthState("authenticated");
        })
        .catch(() => {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          router.replace("/login");
        });
    }

    return unsub;
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Also react to user changes (e.g., after login sets user in store)
  useEffect(() => {
    if (user && authState !== "authenticated") {
      setAuthState("authenticated");
    }
  }, [user, authState]);

  if (authState !== "authenticated") {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-navy">
        <div className="flex flex-col items-center gap-3">
          <div
            className="h-8 w-8 animate-spin rounded-full border-2 border-gold border-t-transparent"
            aria-hidden
          />
          <div className="text-slate-500 dark:text-slate-400">Loading…</div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50 dark:bg-navy">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <TopBar />
        <main className="flex-1 overflow-y-auto p-4 md:p-6 relative">
          {isNavigating && (
            <div className="absolute inset-0 bg-slate-50 dark:bg-navy/50 z-50 flex items-center justify-center backdrop-blur-sm">
              <div className="flex flex-col items-center gap-3">
                <div
                  className="h-8 w-8 animate-spin rounded-full border-2 border-gold border-t-transparent"
                  aria-hidden
                />
                <p className="text-slate-500 dark:text-slate-400">Loading…</p>
              </div>
            </div>
          )}
          {children}
        </main>
      </div>
    </div>
  );
}

