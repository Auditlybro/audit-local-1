"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { companiesApi } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { Building2, ChevronRight, LogOut, Loader2 } from "lucide-react";
import toast from "react-hot-toast";

export default function SelectCompanyPage() {
  const router = useRouter();
  const { user, setCompanyId, setCompanies, setUser } = useAppStore();
  const [isRedirecting, setIsRedirecting] = useState(false);

  const { data: companies, isLoading, error } = useQuery({
    queryKey: ["companies"],
    queryFn: () => companiesApi.list().then((r) => r.data),
    retry: 1,
  });

  const handleSelect = useCallback((id: string) => {
    setIsRedirecting(true);
    setCompanyId(id);
    toast.success("Firm selected successfully");
    setTimeout(() => {
      router.push("/dashboard");
    }, 500);
  }, [router, setCompanyId]);

  useEffect(() => {
    if (companies) {
      setCompanies(companies.map((c) => ({ id: c.id, name: c.name })));
      
      // Auto-select if only one company exists
      if (companies.length === 1 && !isRedirecting) {
        handleSelect(companies[0].id);
      }
    }
  }, [companies, setCompanies, handleSelect, isRedirecting]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    setCompanyId(null);
    router.push("/login");
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-navy">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-gold" />
          <p className="text-slate-500 dark:text-slate-400">Loading your firms...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-navy p-4">
        <div className="max-w-md w-full bg-white dark:bg-navy-400 p-8 rounded-2xl shadow-xl text-center border border-slate-200 dark:border-navy-100/20">
          <div className="h-16 w-16 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <Building2 className="h-8 w-8" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Failed to load firms</h2>
          <p className="text-slate-500 dark:text-slate-400 mb-6">
            There was an error retrieving your organizations. Please try logging in again.
          </p>
          <button
            onClick={handleLogout}
            className="w-full bg-gold hover:bg-gold-light text-navy font-semibold py-2.5 rounded-lg transition-colors"
          >
            Back to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-navy p-4">
      <div className="max-w-xl w-full">
        <div className="mb-8 text-center">
          <h1 className="text-3xl font-bold text-gold mb-2">LedgerX</h1>
          <p className="text-slate-600 dark:text-slate-400 text-lg">
            Welcome back, <span className="text-slate-900 dark:text-white font-semibold">{user?.name || user?.email}</span>
          </p>
          <p className="text-slate-500 dark:text-slate-500 text-sm mt-1">Select a firm to continue to your dashboard</p>
        </div>

        <div className="bg-white dark:bg-navy-400 rounded-2xl shadow-2xl overflow-hidden border border-slate-200 dark:border-navy-100/20">
          <div className="p-6 border-b border-slate-100 dark:border-navy-100/10 flex justify-between items-center bg-slate-50/50 dark:bg-navy-500/30">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">Your Organizations ({companies?.length || 0})</h2>
            <button 
              onClick={handleLogout}
              className="text-xs font-medium text-red-400 hover:text-red-300 flex items-center gap-1 transition-colors"
            >
              <LogOut className="h-3 w-3" />
              Sign Out
            </button>
          </div>

          <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
            {companies && companies.length > 0 ? (
              <div className="divide-y divide-slate-100 dark:divide-navy-100/10">
                {companies.map((company) => (
                  <button
                    key={company.id}
                    onClick={() => handleSelect(company.id)}
                    disabled={isRedirecting}
                    className="w-full p-5 flex items-center gap-4 text-left hover:bg-slate-50 dark:hover:bg-navy-100/10 transition-all group disabled:opacity-50"
                  >
                    <div className="h-12 w-12 rounded-xl bg-gold/10 text-gold flex items-center justify-center group-hover:scale-110 transition-transform shadow-inner">
                      <Building2 className="h-6 w-6" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="font-bold text-slate-900 dark:text-white truncate text-lg">{company.name}</h3>
                      <p className="text-xs text-slate-500 dark:text-slate-500 font-mono mt-0.5">
                        {company.gstin || "No GSTIN linked"}
                      </p>
                    </div>
                    <ChevronRight className="h-5 w-5 text-slate-300 group-hover:text-gold group-hover:translate-x-1 transition-all" />
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-12 text-center">
                <div className="h-16 w-16 bg-slate-100 dark:bg-navy-500 rounded-full flex items-center justify-center mx-auto mb-4 border border-slate-200 dark:border-navy-100/10">
                  <Building2 className="h-8 w-8 text-slate-400" />
                </div>
                <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-1">No organizations found</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 mb-6">You haven&apos;t been added to any firms yet.</p>
                <button
                  onClick={() => router.push("/register?step=3")}
                  className="bg-gold hover:bg-gold-light text-navy px-6 py-2 rounded-lg font-bold transition-all shadow-lg shadow-gold/20"
                >
                  Create New Organization
                </button>
              </div>
            )}
          </div>
        </div>

        <p className="mt-8 text-center text-xs text-slate-500 dark:text-slate-600">
          Logged in as <span className="font-mono">{user?.email}</span>
        </p>
      </div>
      
      {isRedirecting && (
        <div className="fixed inset-0 z-[100] bg-white/60 dark:bg-navy/60 backdrop-blur-md flex flex-col items-center justify-center animate-in fade-in duration-300">
          <Loader2 className="h-12 w-12 animate-spin text-gold mb-4" />
          <h2 className="text-2xl font-bold text-slate-900 dark:text-white tracking-tight">Initializing Dashboard</h2>
          <p className="text-slate-600 dark:text-slate-400 group flex items-center gap-2">
            Loading your financial environment
            <span className="dot-animation inline-flex">
              <span className="animate-bounce delay-0">.</span>
              <span className="animate-bounce delay-75">.</span>
              <span className="animate-bounce delay-150">.</span>
            </span>
          </p>
        </div>
      )}

      <style jsx global>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 6px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: transparent;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #334155;
          border-radius: 10px;
        }
        .dark .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #1e293b;
        }
        .dot-animation span {
          display: inline-block;
          animation: bounce 1s infinite;
        }
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-3px); }
        }
      `}</style>
    </div>
  );
}
