"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAppStore } from "@/lib/store";
import { ChevronDown, LogOut, User, Loader2 } from "lucide-react";
import { useState, useRef, useEffect } from "react";

export function TopBar() {
  const router = useRouter();
  const { user, companyId, companies, setCompanyId, setUser } = useAppStore();
  const [companyOpen, setCompanyOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const companyRef = useRef<HTMLDivElement>(null);
  const userRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (companyRef.current && !companyRef.current.contains(e.target as Node)) setCompanyOpen(false);
      if (userRef.current && !userRef.current.contains(e.target as Node)) setUserOpen(false);
    }
    document.addEventListener("click", handleClick);
    return () => document.removeEventListener("click", handleClick);
  }, []);

  const handleLogout = () => {
    setIsLoggingOut(true);
    setUserOpen(false);
    
    setTimeout(() => {
      if (typeof window !== "undefined") {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
      }
      setUser(null);
      setCompanyId(null);
      router.push("/register"); // Redirect to sign up page as requested
    }, 800);
  };

  const handleCompanySwitch = (id: string) => {
    if (id === companyId) {
      setCompanyOpen(false);
      return;
    }
    setIsSwitching(true);
    setCompanyId(id);
    setCompanyOpen(false);
    
    // Slight delay for the "Wow" factor and to ensure state propagates
    setTimeout(() => {
      router.push("/dashboard");
      // The actual navigation will re-mount the page, effectively clearing this state
      // but we'll reset it anyway as a fallback
      setIsSwitching(false);
    }, 800);
  };

  const currentCompany = companies.find((c) => c.id === companyId);

  return (
    <header className="h-14 border-b border-slate-200 dark:border-navy-100/20 bg-slate-50 dark:bg-navy-300 flex items-center justify-between px-4 relative">
      {(isSwitching || isLoggingOut) && (
        <div className="fixed inset-0 z-[100] bg-white/60 dark:bg-navy/60 backdrop-blur-md flex flex-col items-center justify-center animate-in fade-in duration-300">
          <Loader2 className="h-10 w-10 animate-spin text-gold mb-3" />
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">
            {isLoggingOut ? "Signing Out" : "Switching Firm"}
          </h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            {isLoggingOut ? "Logging out safely..." : "Loading company environment..."}
          </p>
        </div>
      )}
      
      <div className="flex items-center gap-4">
        <div className="relative" ref={companyRef}>
          <button
            type="button"
            onClick={() => setCompanyOpen((o) => !o)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 dark:bg-navy-100/30 text-slate-200 hover:bg-slate-100 dark:bg-navy-100/50 min-w-[200px] border border-slate-200 dark:border-navy-100/20 shadow-sm transition-all"
          >
            <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="truncate flex-1 text-left font-medium">{currentCompany?.name ?? "Select company"}</span>
            <ChevronDown className="w-4 h-4 shrink-0 opacity-50" />
          </button>
          {companyOpen && companies.length > 0 && (
            <div className="absolute top-full left-0 mt-1 w-72 rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400 shadow-2xl py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
              <div className="px-3 py-1 mb-1 text-[10px] font-bold uppercase tracking-wider text-slate-500">Available Firms</div>
              <div className="max-h-60 overflow-y-auto">
                {companies.map((c) => (
                  <button
                    key={c.id}
                    type="button"
                    onClick={() => handleCompanySwitch(c.id)}
                    className={`flex items-center justify-between w-full text-left px-3 py-2.5 text-sm transition-colors ${
                      c.id === companyId 
                        ? "bg-gold/10 text-gold font-semibold" 
                        : "text-slate-200 hover:bg-slate-100 dark:hover:bg-navy-100/20"
                    }`}
                  >
                    <span className="truncate">{c.name}</span>
                    {c.id === companyId && <div className="h-1.5 w-1.5 rounded-full bg-gold" />}
                  </button>
                ))}
              </div>
              <div className="mt-1 pt-1 border-t border-slate-100 dark:border-navy-100/10">
                <Link
                  href="/register?step=3"
                  className="block px-3 py-2 text-xs font-medium text-gold hover:bg-slate-100 dark:hover:bg-navy-100/20 transition-colors"
                  onClick={() => setCompanyOpen(false)}
                >
                  + Register New Company
                </Link>
              </div>
            </div>
          )}
        </div>
      </div>
      <div className="relative" ref={userRef}>
        <button
          type="button"
          onClick={() => setUserOpen((o) => !o)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-100 dark:bg-navy-100/30"
        >
          <User className="w-5 h-5" />
          <span className="text-sm">{user?.name || user?.email || "User"}</span>
          <ChevronDown className="w-4 h-4" />
        </button>
        {userOpen && (
          <div className="absolute right-0 top-full mt-1 w-56 rounded-lg border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400 shadow-xl py-1 z-50">
            <div className="px-3 py-2 text-sm text-slate-500 dark:text-slate-400 border-b border-slate-200 dark:border-navy-100/20">
              {user?.email}
            </div>
            <button
              type="button"
              onClick={handleLogout}
              className="flex w-full items-center gap-2 px-3 py-2 text-sm text-slate-200 hover:bg-slate-100 dark:bg-navy-100/30"
            >
              <LogOut className="w-4 h-4" />
              Log out
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
