"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { format } from "date-fns";

export default function LedgerReportPage() {
  const params = useParams();
  const id = params.id as string;
  const companyId = useAppStore((s) => s.companyId);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 3, 1));
  const [toDate, setToDate] = useState(new Date());

  const { data } = useQuery({
    queryKey: ["ledger-report", companyId, id, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")],
    queryFn: () => reportsApi.ledger(companyId!, id, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")).then((r) => r.data),
    enabled: !!companyId && !!id,
  });

  const d = data as { ledger_name?: string; opening_balance?: number; rows?: { date: string; voucher_type: string; number: string; debit: number; credit: number; balance: number }[]; closing_balance?: number } | undefined;

  return (
    <ReportWrapper title={`Ledger: ${d?.ledger_name ?? id}`} fromDate={fromDate} toDate={toDate} onFromChange={setFromDate} onToChange={setToDate} onExportExcel={() => {}} onExportPdf={() => {}} onPrint={() => window.print()}>
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <div className="bg-navy-100/20 px-4 py-2 text-slate-400">Opening balance: <AmountDisplay amount={d?.opening_balance} /></div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-navy-100/20 bg-navy-400">
              <th className="px-4 py-3 text-left text-slate-400">Date</th>
              <th className="px-4 py-3 text-left text-slate-400">Type</th>
              <th className="px-4 py-3 text-left text-slate-400">Number</th>
              <th className="px-4 py-3 text-right text-slate-400">Debit</th>
              <th className="px-4 py-3 text-right text-slate-400">Credit</th>
              <th className="px-4 py-3 text-right text-slate-400">Balance</th>
            </tr>
          </thead>
          <tbody>
            {(d?.rows ?? []).map((r, i) => (
              <tr key={i} className="border-b border-navy-100/10">
                <td className="px-4 py-2 text-slate-200">{r.date}</td>
                <td className="px-4 py-2 text-slate-200">{r.voucher_type}</td>
                <td className="px-4 py-2 text-slate-200">{r.number}</td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.debit} showZero={false} /></td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.credit} showZero={false} /></td>
                <td className="px-4 py-2 text-right font-number text-gold"><AmountDisplay amount={r.balance} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="bg-navy-100/20 px-4 py-2 text-gold font-number">Closing balance: <AmountDisplay amount={d?.closing_balance} /></div>
      </div>
    </ReportWrapper>
  );
}
