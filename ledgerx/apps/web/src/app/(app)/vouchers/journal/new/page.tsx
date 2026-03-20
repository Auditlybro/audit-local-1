"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ledgersApi, vouchersApi } from "@/lib/api";
import { format } from "date-fns";
import { Plus, Trash2 } from "lucide-react";

type JournalRow = { id: string; ledger_id: string; dr: number; cr: number; narration: string };

export default function NewJournalPage() {
  const companyId = useAppStore((s) => s.companyId);
  const queryClient = useQueryClient();
  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [narration, setNarration] = useState("");
  const [rows, setRows] = useState<JournalRow[]>([
    { id: crypto.randomUUID(), ledger_id: "", dr: 0, cr: 0, narration: "" },
    { id: crypto.randomUUID(), ledger_id: "", dr: 0, cr: 0, narration: "" },
  ]);

  const { data: ledgers = [] } = useQuery({
    queryKey: ["ledgers", companyId],
    queryFn: () => ledgersApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const totalDr = rows.reduce((s, r) => s + r.dr, 0);
  const totalCr = rows.reduce((s, r) => s + r.cr, 0);
  const balanced = Math.abs(totalDr - totalCr) < 0.01;

  const addRow = () => setRows((r) => [...r, { id: crypto.randomUUID(), ledger_id: "", dr: 0, cr: 0, narration: "" }]);
  const updateRow = (id: string, u: Partial<JournalRow>) => setRows((r) => r.map((x) => (x.id === id ? { ...x, ...u } : x)));
  const removeRow = (id: string) => setRows((r) => r.filter((x) => x.id !== id));

  const createJournal = useMutation({
    mutationFn: () =>
      vouchersApi.create(companyId!, {
        voucher_type: "JOURNAL",
        date,
        narration: narration || undefined,
        entries: rows.filter((e) => e.ledger_id && (e.dr > 0 || e.cr > 0)).map((e) => ({ ledger_id: e.ledger_id, dr_amount: e.dr, cr_amount: e.cr, narration: e.narration || undefined })),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vouchers", companyId] });
      window.history.back();
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Journal Entry</h1>
      <div className="flex gap-4">
        <div>
          <label className="block text-sm text-slate-400">Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="mt-1 rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white" />
        </div>
        <div className="flex-1">
          <label className="block text-sm text-slate-400">Narration</label>
          <input type="text" value={narration} onChange={(e) => setNarration(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white" />
        </div>
      </div>
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <div className="flex justify-between items-center p-4 bg-navy-100/20">
          <h2 className="font-semibold text-white">Dr / Cr entries (must balance)</h2>
          <button type="button" onClick={addRow} className="flex items-center gap-1 rounded-lg bg-gold px-3 py-1.5 text-sm text-navy"><Plus className="h-4 w-4" /> Add row</button>
        </div>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-navy-100/20 bg-navy-400">
              <th className="px-3 py-2 text-left text-slate-400">Ledger</th>
              <th className="px-3 py-2 text-right text-slate-400">Debit</th>
              <th className="px-3 py-2 text-right text-slate-400">Credit</th>
              <th className="px-3 py-2 text-left text-slate-400">Narration</th>
              <th className="w-10" />
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-b border-navy-100/10">
                <td className="px-3 py-2">
                  <select
                    value={row.ledger_id}
                    onChange={(e) => updateRow(row.id, { ledger_id: e.target.value })}
                    className="w-full max-w-[200px] rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-white"
                  >
                    <option value="">Select</option>
                    {ledgers.map((l) => (
                      <option key={l.id} value={l.id}>{l.name}</option>
                    ))}
                  </select>
                </td>
                <td className="px-3 py-2">
                  <input type="number" min={0} step={0.01} value={row.dr || ""} onChange={(e) => updateRow(row.id, { dr: parseFloat(e.target.value) || 0, cr: 0 })} className="w-28 rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-right text-white font-number" />
                </td>
                <td className="px-3 py-2">
                  <input type="number" min={0} step={0.01} value={row.cr || ""} onChange={(e) => updateRow(row.id, { cr: parseFloat(e.target.value) || 0, dr: 0 })} className="w-28 rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-right text-white font-number" />
                </td>
                <td className="px-3 py-2">
                  <input type="text" value={row.narration} onChange={(e) => updateRow(row.id, { narration: e.target.value })} className="w-full rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-white" />
                </td>
                <td className="px-3 py-2">
                  <button type="button" onClick={() => removeRow(row.id)} className="text-slate-500 hover:text-red-400"><Trash2 className="h-4 w-4" /></button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="flex justify-end gap-4 px-4 py-2 bg-navy-100/10 text-sm">
          <span className={balanced ? "text-emerald-400" : "text-red-400"}>Total Dr: ₹{totalDr.toFixed(2)}</span>
          <span className={balanced ? "text-emerald-400" : "text-red-400"}>Total Cr: ₹{totalCr.toFixed(2)}</span>
          {!balanced && <span className="text-red-400">Must be equal to save</span>}
        </div>
      </div>
      <button
        type="button"
        onClick={() => createJournal.mutate()}
        disabled={createJournal.isPending || !balanced}
        className="rounded-lg bg-gold px-4 py-2 font-medium text-navy disabled:opacity-50"
      >
        {createJournal.isPending ? "Saving…" : "Save Journal"}
      </button>
    </div>
  );
}
