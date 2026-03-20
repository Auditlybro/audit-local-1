"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { gstApi } from "@/lib/api";
import { Download } from "lucide-react";

export default function Gstr1Page() {
  const companyId = useAppStore((s) => s.companyId);
  const [period, setPeriod] = useState("2025-04");

  useQuery({
    queryKey: ["gstr1", companyId, period],
    queryFn: () => gstApi.gstr1(companyId!, period.replace("-", "-")).then((r) => r.data),
    enabled: !!companyId,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">GSTR-1</h1>
      <div className="flex gap-4">
        <input type="month" value={period} onChange={(e) => setPeriod(e.target.value)} className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white" />
        <button type="button" className="flex items-center gap-2 rounded-lg bg-gold px-4 py-2 text-navy"> <Download className="h-4 w-4" /> JSON download </button>
        <button type="button" className="rounded-lg border border-navy-100/30 px-4 py-2 text-slate-200">Upload to portal</button>
      </div>
      <p className="text-slate-500 text-sm">B2B, B2C, HSN tables — connect to API data</p>
    </div>
  );
}
