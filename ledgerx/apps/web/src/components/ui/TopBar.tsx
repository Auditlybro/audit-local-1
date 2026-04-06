"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAppStore } from "@/lib/store";
import { ChevronDown, LogOut, User } from "lucide-react";
import { useState, useRef, useEffect } from "react";

export function TopBar() {
  const router = useRouter();
  const { user, companyId, companies, setCompanyId, setUser } = useAppStore();
  const [companyOpen, setCompanyOpen] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
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
    if (typeof window !== "undefined") {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
    }
    setUser(null);
    setCompanyId(null);
    router.push("/login");
  };

  const currentCompany = companies.find((c) => c.id === companyId);

  return (
    <header className="h-14 border-b border-slate-200 dark:border-navy-100/20 bg-slate-50 dark:bg-navy-300 flex items-center justify-between px-4">
      <div className="flex items-center gap-4">
        <div className="relative" ref={companyRef}>
          <button
            type="button"
            onClick={() => setCompanyOpen((o) => !o)}
            className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-100 dark:bg-navy-100/30 text-slate-200 hover:bg-slate-100 dark:bg-navy-100/50 min-w-[180px]"
          >
            <span className="truncate">{currentCompany?.name ?? "Select company"}</span>
            <ChevronDown className="w-4 h-4 shrink-0" />
          </button>
          {companyOpen && companies.length > 0 && (
            <div className="absolute top-full left-0 mt-1 w-64 rounded-lg border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400 shadow-xl py-1 z-50">
              {companies.map((c) => (
                <button
                  key={c.id}
                  type="button"
                  onClick={() => {
                    setCompanyId(c.id);
                    setCompanyOpen(false);
                  }}
                  className="block w-full text-left px-3 py-2 text-sm text-slate-200 hover:bg-slate-100 dark:bg-navy-100/30"
                >
                  {c.name}
                </button>
              ))}
              <Link
                href="/dashboard"
                className="block px-3 py-2 text-sm text-gold hover:bg-slate-100 dark:bg-navy-100/30"
                onClick={() => setCompanyOpen(false)}
              >
                + Add company
              </Link>
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
