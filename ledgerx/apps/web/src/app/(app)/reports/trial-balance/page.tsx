"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { format } from "date-fns";

export default function TrialBalancePage() {
  const companyId = useAppStore((s) => s.companyId);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 3, 1));
  const [toDate, setToDate] = useState(new Date());

  const { data } = useQuery({
    queryKey: ["trial-balance", companyId, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")],
    queryFn: () => reportsApi.trialBalance(companyId!, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")).then((r) => r.data),
    enabled: !!companyId,
  });

  const rows = (data as { rows?: { ledger_name: string; group_name: string; debit: number; credit: number }[] })?.rows ?? [];
  const totalDebit = (data as { total_debit?: number })?.total_debit ?? 0;
  const totalCredit = (data as { total_credit?: number })?.total_credit ?? 0;

  return (
    <ReportWrapper
      title="Trial Balance"
      fromDate={fromDate}
      toDate={toDate}
      onFromChange={setFromDate}
      onToChange={setToDate}
      onExportExcel={() => {}}
      onExportPdf={() => {}}
      onPrint={() => window.print()}
    >
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-navy-100/20 bg-navy-100/20">
              <th className="px-4 py-3 text-left text-slate-400">Ledger</th>
              <th className="px-4 py-3 text-left text-slate-400">Group</th>
              <th className="px-4 py-3 text-right text-slate-400">Debit</th>
              <th className="px-4 py-3 text-right text-slate-400">Credit</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-b border-navy-100/10">
                <td className="px-4 py-2 text-slate-200">{r.ledger_name}</td>
                <td className="px-4 py-2 text-slate-400">{r.group_name}</td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.debit} showZero={false} /></td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.credit} showZero={false} /></td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t border-gold/30 bg-navy-100/20 font-medium">
              <td colSpan={2} className="px-4 py-3 text-slate-200">Total</td>
              <td className="px-4 py-3 text-right font-number text-gold"><AmountDisplay amount={totalDebit} /></td>
              <td className="px-4 py-3 text-right font-number text-gold"><AmountDisplay amount={totalCredit} /></td>
            </tr>
          </tfoot>
        </table>
      </div>
    </ReportWrapper>
  );
}
