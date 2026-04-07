"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { format } from "date-fns";

export default function ProfitLossPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 3, 1));
  const [toDate, setToDate] = useState(new Date());

  const { data } = useQuery({
    queryKey: ["profit-loss", companyId, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")],
    queryFn: () => reportsApi.profitLoss(companyId!, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")).then((r) => r.data),
    enabled: !!companyId,
  });

  const d = data as { revenue?: number; expenses?: number; net_profit?: number } | undefined;

  return (
    <ReportWrapper title="Profit & Loss" fromDate={fromDate} toDate={toDate} onFromChange={setFromDate} onToChange={setToDate} onExportExcel={() => {}} onExportPdf={() => {}} onPrint={() => window.print()}>
      <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-6 max-w-md space-y-4">
        <div className="flex justify-between"><span className="text-slate-500 dark:text-slate-400">Revenue</span><AmountDisplay amount={d?.revenue} /></div>
        <div className="flex justify-between"><span className="text-slate-500 dark:text-slate-400">Expenses</span><AmountDisplay amount={d?.expenses} /></div>
        <div className="flex justify-between pt-2 border-t border-slate-200 dark:border-navy-100/20 font-semibold text-gold">Net Profit<AmountDisplay amount={d?.net_profit} /></div>
      </div>
    </ReportWrapper>
  );
}
