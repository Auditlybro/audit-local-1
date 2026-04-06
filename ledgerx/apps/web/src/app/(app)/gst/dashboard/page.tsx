"use client";

import { useAppStore } from "@/lib/store";
import { Calendar, FileCheck } from "lucide-react";

export default function GstDashboardPage() {
  useAppStore((s) => s.companyId);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">GST Dashboard</h1>
      <p className="text-slate-500 dark:text-slate-400">Filing calendar, status per return. Connect to GST API.</p>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-6">
          <Calendar className="h-10 w-10 text-gold mb-2" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Filing calendar</h2>
          <p className="mt-2 text-sm text-slate-500">GSTR-1, GSTR-3B due dates by period</p>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-6">
          <FileCheck className="h-10 w-10 text-gold mb-2" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Return status</h2>
          <p className="mt-2 text-sm text-slate-500">Status per return type and period</p>
        </div>
      </div>
    </div>
  );
}
