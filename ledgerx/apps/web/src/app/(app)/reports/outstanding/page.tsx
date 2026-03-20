"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";

export default function OutstandingPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [tab, setTab] = useState<"receivables" | "payables">("receivables");

  const { data: receivables } = useQuery({
    queryKey: ["outstanding-receivables", companyId],
    queryFn: () => reportsApi.outstandingReceivables(companyId!).then((r) => r.data),
    enabled: !!companyId && tab === "receivables",
  });
  const { data: payables } = useQuery({
    queryKey: ["outstanding-payables", companyId],
    queryFn: () => reportsApi.outstandingPayables(companyId!).then((r) => r.data),
    enabled: !!companyId && tab === "payables",
  });

  const items = (tab === "receivables" ? (receivables as { items?: { name: string; amount: number }[] })?.items : (payables as { items?: { name: string; amount: number }[] })?.items) ?? [];

  return (
    <ReportWrapper title="Outstanding" onExportExcel={() => {}} onExportPdf={() => {}} onPrint={() => window.print()}>
      <div className="flex gap-2 mb-4">
        <button type="button" onClick={() => setTab("receivables")} className={`rounded-lg px-4 py-2 text-sm ${tab === "receivables" ? "bg-gold text-navy" : "bg-navy-100/30 text-slate-400"}`}>Receivables</button>
        <button type="button" onClick={() => setTab("payables")} className={`rounded-lg px-4 py-2 text-sm ${tab === "payables" ? "bg-gold text-navy" : "bg-navy-100/30 text-slate-400"}`}>Payables</button>
      </div>
      <p className="text-slate-500 text-sm mb-4">Ageing: 0-30 | 30-60 | 60-90 | 90+ days (connect to API)</p>
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-navy-100/20 bg-navy-100/20"><th className="px-4 py-3 text-left text-slate-400">Party</th><th className="px-4 py-3 text-right text-slate-400">Amount</th></tr></thead>
          <tbody>
            {items.map((item, i) => (
              <tr key={i} className="border-b border-navy-100/10"><td className="px-4 py-2 text-slate-200">{item.name}</td><td className="px-4 py-2 text-right font-number"><AmountDisplay amount={item.amount} /></td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </ReportWrapper>
  );
}
