"use client";

import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { reportsApi } from "@/lib/api";
import { ReportWrapper } from "@/components/ui/ReportWrapper";
import { AmountDisplay } from "@/components/ui/AmountDisplay";

export default function StockSummaryPage() {
  const companyId = useAppStore((s) => s.companyId);
  const { data } = useQuery({
    queryKey: ["stock-summary", companyId],
    queryFn: () => reportsApi.stockSummary(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const rows = (data as { rows?: { item_name: string; quantity: number; value: number }[] } | undefined)?.rows ?? [];

  return (
    <ReportWrapper title="Stock Summary" onExportExcel={() => {}} onExportPdf={() => {}} onPrint={() => window.print()}>
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-navy-100/20 bg-navy-100/20">
              <th className="px-4 py-3 text-left text-slate-400">Item</th>
              <th className="px-4 py-3 text-right text-slate-400">Quantity</th>
              <th className="px-4 py-3 text-right text-slate-400">Value</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r, i) => (
              <tr key={i} className="border-b border-navy-100/10">
                <td className="px-4 py-2 text-slate-200">{r.item_name}</td>
                <td className="px-4 py-2 text-right font-number">{r.quantity}</td>
                <td className="px-4 py-2 text-right font-number"><AmountDisplay amount={r.value} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </ReportWrapper>
  );
}
