"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { format } from "date-fns";

export default function SalesRegisterPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [fromDate, setFromDate] = useState(new Date(new Date().getFullYear(), 3, 1));
  const [toDate, setToDate] = useState(new Date());

  const { data } = useQuery({
    queryKey: ["sales-register", companyId, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")],
    queryFn: () => reportsApi.salesRegister(companyId!, format(fromDate, "yyyy-MM-dd"), format(toDate, "yyyy-MM-dd")).then((r) => r.data),
    enabled: !!companyId,
  });

  const rows = (data as { rows?: { date: string; number: string; taxable_value: number; gst: number; total: number }[] })?.rows ?? [];

  return (
    <ReportWrapper title="Sales Register" fromDate={fromDate} toDate={toDate} onFromChange={setFromDate} onToChange={setToDate} onExportExcel={() => {}} onExportPdf={() => {}} onPrint={() => window.print()}>
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-navy-100/20 bg-navy-100/20">
              <th className="px-4 py-3 text-left text-slate-400">Date</th>
              <th className="px-4 py-3 text-left text-slate-400">Number</th>
              <th className="px-4 py-3 text-right text-slate-400">Taxable</th>
              <th className="px-4 py-3 text-right text-slate-400">GST</th>
              <th className="px-4 py-3 text-right text-slate-400">Total</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-b border-navy-100/10">
                <td className="px-4 py-2 text-slate-200">{r.date}</td>
                <td className="px-4 py-2 text-slate-200">{r.number}</td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.taxable_value} /></td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.gst} /></td>
                <td className="px-4 py-2 text-right font-number text-gold"><AmountDisplay amount={r.total} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ReportWrapper>
  );
}
