"use client";

import { useAppStore } from "@/lib/store";
import { Users, Plus } from "lucide-react";

export default function CaClientsPage() {
  const companies = useAppStore((s) => s.companies);

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">CA — Clients</h1>
        <button type="button" className="flex items-center gap-2 rounded-lg bg-gold px-4 py-2 text-navy"><Plus className="h-4 w-4" /> Add company</button>
      </div>
      <p className="text-slate-500 dark:text-slate-400">All client companies. Add company | Switch to company. (Show when user role = CA)</p>
      <div className="grid gap-4 md:grid-cols-2">
        {companies.map((c) => (
          <div key={c.id} className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4 flex items-center gap-3">
            <Users className="h-10 w-10 text-gold" />
            <div>
              <p className="font-medium text-slate-900 dark:text-white">{c.name}</p>
              <p className="text-sm text-slate-500">Switch to company</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
