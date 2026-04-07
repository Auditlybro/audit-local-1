"use client";

import { useTheme } from "next-themes";
import { Moon, Sun } from "lucide-react";
import clsx from "clsx";
import { useEffect, useState } from "react";

export default function SettingsPage() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
          Settings
        </h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          Manage your application preferences and settings.
        </p>
      </div>

      <div className="space-y-6">
        <section className="bg-white dark:bg-navy-400 rounded-xl border border-slate-200 dark:border-navy-100/20 overflow-hidden shadow-sm">
          <div className="p-6 border-b border-slate-200 dark:border-navy-100/20">
            <h2 className="text-xl font-semibold text-slate-800 dark:text-slate-200">
              Appearance
            </h2>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
              Customize the look and feel of LedgerX.
            </p>
          </div>

          <div className="p-6">
            <div className="flex flex-col sm:flex-row gap-4 max-w-lg">
              <button
                onClick={() => setTheme("light")}
                className={clsx(
                  "flex-1 flex flex-col items-center justify-center gap-3 p-6 rounded-lg border-2 transition-all",
                  theme === "light"
                    ? "border-gold bg-gold/5"
                    : "border-slate-200 hover:border-slate-300 dark:border-navy-100/30 dark:hover:border-navy-100/50 bg-transparent",
                )}
              >
                <div className="p-3 bg-white border border-slate-200 text-slate-700 rounded-full shadow-sm">
                  <Sun className="w-6 h-6" />
                </div>
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  Light
                </span>
              </button>

              <button
                onClick={() => setTheme("dark")}
                className={clsx(
                  "flex-1 flex flex-col items-center justify-center gap-3 p-6 rounded-lg border-2 transition-all",
                  theme === "dark"
                    ? "border-gold bg-gold/10"
                    : "border-slate-200 hover:border-slate-300 dark:border-navy-100/30 dark:hover:border-navy-100/50 bg-transparent",
                )}
              >
                <div className="p-3 bg-[#0d1321] border border-[#1b263b] text-slate-200 rounded-full shadow-inner">
                  <Moon className="w-6 h-6" />
                </div>
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  Dark
                </span>
              </button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
