"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { gstApi } from "@/lib/api";

export default function Gstr3bPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [period, setPeriod] = useState("04-2025");

  useQuery({
    queryKey: ["gstr3b", companyId, period],
    queryFn: () => gstApi.gstr3b(companyId!, period).then((r) => r.data),
    enabled: !!companyId,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">GSTR-3B</h1>
      <input type="month" value={period} onChange={(e) => setPeriod(e.target.value)} className="rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-slate-900 dark:text-white" />
      <p className="text-slate-500">Auto-populated form. Connect to API.</p>
    </div>
  );
}
