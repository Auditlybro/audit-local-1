"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { importApi } from "@/lib/api";
import { FileCode, FileSpreadsheet, Landmark } from "lucide-react";

export default function ImportPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [drag, setDrag] = useState(false);

  const { data: history } = useQuery({
    queryKey: ["import-history", companyId],
    queryFn: () => importApi.history(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const sessions = (history as { sessions?: { id: string; source_type: string; status: string; total_records: number; imported_records: number; created_at: string }[] })?.sessions ?? [];

  return (
    <div className="space-y-8">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Import Data</h1>

      <div className="grid gap-6 md:grid-cols-3">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-6">
          <FileCode className="h-12 w-12 text-gold mb-4" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Import from Tally XML</h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Drag & drop .xml files. Preview before commit.</p>
          <div
            onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
            onDragLeave={() => setDrag(false)}
            onDrop={(e) => { e.preventDefault(); setDrag(false); }}
            className={`mt-4 rounded-lg border-2 border-dashed py-8 text-center text-slate-500 ${drag ? "border-gold bg-gold/10" : "border-slate-200 dark:border-navy-100/30"}`}
          >
            Drop .xml here or click to browse
          </div>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-6">
          <FileSpreadsheet className="h-12 w-12 text-gold mb-4" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Marg / Busy / Excel</h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">Same flow, different parsers.</p>
          <div className="mt-4 rounded-lg border-2 border-dashed border-slate-200 dark:border-navy-100/30 py-8 text-center text-slate-500">Drop file here</div>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-6">
          <Landmark className="h-12 w-12 text-gold mb-4" />
          <h2 className="font-semibold text-slate-900 dark:text-white">Bank Statement</h2>
          <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">CSV/Excel, auto-detect format.</p>
          <div className="mt-4 rounded-lg border-2 border-dashed border-slate-200 dark:border-navy-100/30 py-8 text-center text-slate-500">Drop file here</div>
        </div>
      </div>

      <div>
        <h2 className="font-semibold text-slate-900 dark:text-white mb-4">Import History</h2>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 overflow-hidden">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-slate-200 dark:border-navy-100/20 bg-slate-100 dark:bg-navy-100/20"><th className="px-4 py-3 text-left text-slate-500 dark:text-slate-400">Source</th><th className="px-4 py-3 text-left text-slate-500 dark:text-slate-400">Status</th><th className="px-4 py-3 text-right text-slate-500 dark:text-slate-400">Records</th><th className="px-4 py-3 text-left text-slate-500 dark:text-slate-400">Date</th></tr></thead>
            <tbody>
              {sessions.map((s) => (
                <tr key={s.id} className="border-b border-slate-200 dark:border-navy-100/10">
                  <td className="px-4 py-2 text-slate-200">{s.source_type}</td>
                  <td className="px-4 py-2 text-slate-200">{s.status}</td>
                  <td className="px-4 py-2 text-right text-slate-200">{s.imported_records} / {s.total_records}</td>
                  <td className="px-4 py-2 text-slate-500 dark:text-slate-400">{s.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
