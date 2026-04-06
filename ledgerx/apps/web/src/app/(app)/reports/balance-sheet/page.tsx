"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { format } from "date-fns";

export default function BalanceSheetPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [asOn, setAsOn] = useState(new Date());
  const [formatToggle, setFormatToggle] = useState<"tally" | "icai">("tally");

  const { data } = useQuery({
    queryKey: ["balance-sheet", companyId, format(asOn, "yyyy-MM-dd")],
    queryFn: () => reportsApi.balanceSheet(companyId!, format(asOn, "yyyy-MM-dd")).then((r) => r.data),
    enabled: !!companyId,
  });

  const assets = (data as { assets?: { name: string; amount: number }[] })?.assets ?? [];
  const liabilities = (data as { liabilities?: { name: string; amount: number }[] })?.liabilities ?? [];

  return (
    <ReportWrapper title="Balance Sheet" mode="single" singleDate={asOn} onSingleDateChange={setAsOn} onExportExcel={() => {}} onExportPdf={() => {}} onPrint={() => window.print()}>
      <div className="flex gap-2 mb-4">
        <button type="button" onClick={() => setFormatToggle("tally")} className={`rounded-lg px-3 py-1.5 text-sm ${formatToggle === "tally" ? "bg-gold text-navy" : "bg-slate-100 dark:bg-navy-100/30 text-slate-500 dark:text-slate-400"}`}>Tally format</button>
        <button type="button" onClick={() => setFormatToggle("icai")} className={`rounded-lg px-3 py-1.5 text-sm ${formatToggle === "icai" ? "bg-gold text-navy" : "bg-slate-100 dark:bg-navy-100/30 text-slate-500 dark:text-slate-400"}`}>ICAI format</button>
      </div>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 overflow-hidden">
          <div className="bg-slate-100 dark:bg-navy-100/20 px-4 py-2 font-semibold text-gold">Assets</div>
          <ul className="divide-y divide-navy-100/10">
            {assets.map((a, i) => (
              <li key={i} className="flex justify-between px-4 py-2 text-slate-200"><span>{a.name}</span><AmountDisplay amount={a.amount} /></li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 overflow-hidden">
          <div className="bg-slate-100 dark:bg-navy-100/20 px-4 py-2 font-semibold text-gold">Liabilities</div>
          <ul className="divide-y divide-navy-100/10">
            {liabilities.map((l, i) => (
              <li key={i} className="flex justify-between px-4 py-2 text-slate-200"><span>{l.name}</span><AmountDisplay amount={l.amount} /></li>
            ))}
          </ul>
        </div>
      </div>
    </ReportWrapper>
  );
}
