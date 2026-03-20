"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ledgersApi, stockApi, vouchersApi } from "@/lib/api";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { format } from "date-fns";
import { Plus, Trash2 } from "lucide-react";

type Row = {
  id: string;
  stock_item_id: string;
  name: string;
  qty: number;
  rate: number;
  discount_pct: number;
  gst_rate: number;
  taxable: number;
  cgst: number;
  sgst: number;
  igst: number;
  total: number;
};

export default function NewSalePage() {
  const companyId = useAppStore((s) => s.companyId);
  const queryClient = useQueryClient();
  const [partyId, setPartyId] = useState("");
  const [partySearch, setPartySearch] = useState("");
  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [rows, setRows] = useState<Row[]>([]);
  const [saveAs, setSaveAs] = useState<"draft" | "final" | "repeat">("final");

  const { data: ledgers = [] } = useQuery({
    queryKey: ["ledgers", companyId],
    queryFn: () => ledgersApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });
  const { data: stockItems = [] } = useQuery({
    queryKey: ["stock-items", companyId],
    queryFn: () => stockApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const addRow = () => {
    const first = stockItems[0];
    setRows((r) => [
      ...r,
      {
        id: crypto.randomUUID(),
        stock_item_id: first?.id ?? "",
        name: first?.name ?? "",
        qty: 1,
        rate: 0,
        discount_pct: 0,
        gst_rate: 18,
        taxable: 0,
        cgst: 0,
        sgst: 0,
        igst: 0,
        total: 0,
      },
    ]);
  };

  const updateRow = (id: string, updates: Partial<Row>) => {
    setRows((r) =>
      r.map((row) => {
        if (row.id !== id) return row;
        const next = { ...row, ...updates };
        const taxable = next.qty * next.rate * (1 - next.discount_pct / 100);
        const tax = (taxable * (next.gst_rate || 0)) / 100;
        next.taxable = Math.round(taxable * 100) / 100;
        next.cgst = next.sgst = Math.round((tax / 2) * 100) / 100;
        next.igst = 0;
        next.total = Math.round((taxable + tax) * 100) / 100;
        return next;
      })
    );
  };

  const removeRow = (id: string) => setRows((r) => r.filter((x) => x.id !== id));

  const subtotal = rows.reduce((s, x) => s + x.taxable, 0);
  const totalTax = rows.reduce((s, x) => s + x.cgst + x.sgst + x.igst, 0);
  const netTotal = rows.reduce((s, x) => s + x.total, 0);

  const createVoucher = useMutation({
    mutationFn: () =>
      vouchersApi.create(companyId!, {
        voucher_type: "SALES",
        date,
        party_ledger_id: partyId || undefined,
        entries: [], // Would build from rows + party + tax ledgers
        invoice_items: rows.map((row) => ({
          stock_item_id: row.stock_item_id,
          quantity: row.qty,
          rate: row.rate,
          taxable_value: row.taxable,
          cgst_rate: row.gst_rate / 2,
          cgst_amount: row.cgst,
          sgst_rate: row.gst_rate / 2,
          sgst_amount: row.sgst,
          igst_rate: 0,
          igst_amount: 0,
          total_amount: row.total,
        })),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vouchers", companyId] });
      window.history.back();
    },
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">New Sale</h1>

      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <label className="block text-sm text-slate-400">Party (Ledger)</label>
          <input
            type="text"
            placeholder="Search ledger..."
            value={partySearch}
            onChange={(e) => setPartySearch(e.target.value)}
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
          />
          <select
            value={partyId}
            onChange={(e) => setPartyId(e.target.value)}
            className="mt-2 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
          >
            <option value="">Select party</option>
            {ledgers.filter((l) => l.name.toLowerCase().includes(partySearch.toLowerCase())).map((l) => (
              <option key={l.id} value={l.id}>{l.name}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400">Date</label>
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
          />
        </div>
      </div>

      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <div className="flex justify-between items-center p-4 bg-navy-100/20">
          <h2 className="font-semibold text-white">Items</h2>
          <button type="button" onClick={addRow} className="flex items-center gap-1 rounded-lg bg-gold px-3 py-1.5 text-sm text-navy">
            <Plus className="h-4 w-4" /> Add row
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-navy-100/20 bg-navy-400">
                <th className="px-3 py-2 text-left text-slate-400">Item</th>
                <th className="px-3 py-2 text-right text-slate-400">Qty</th>
                <th className="px-3 py-2 text-right text-slate-400">Rate</th>
                <th className="px-3 py-2 text-right text-slate-400">Disc%</th>
                <th className="px-3 py-2 text-right text-slate-400">Taxable</th>
                <th className="px-3 py-2 text-right text-slate-400">GST%</th>
                <th className="px-3 py-2 text-right text-slate-400">CGST/SGST</th>
                <th className="px-3 py-2 text-right text-slate-400">Total</th>
                <th className="w-10" />
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.id} className="border-b border-navy-100/10">
                  <td className="px-3 py-2">
                    <select
                      value={row.stock_item_id}
                      onChange={(e) => {
                        const item = stockItems.find((i) => i.id === e.target.value);
                        updateRow(row.id, { stock_item_id: e.target.value, name: item?.name ?? "", rate: item?.mrp ?? 0, gst_rate: item?.gst_rate ?? 18 });
                      }}
                      className="w-full max-w-[180px] rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-white"
                    >
                      {stockItems.map((i) => (
                        <option key={i.id} value={i.id}>{i.name}</option>
                      ))}
                    </select>
                  </td>
                  <td className="px-3 py-2 text-right">
                    <input
                      type="number"
                      min={0}
                      step={0.01}
                      value={row.qty}
                      onChange={(e) => updateRow(row.id, { qty: parseFloat(e.target.value) || 0 })}
                      className="w-20 rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-right text-white"
                    />
                  </td>
                  <td className="px-3 py-2 text-right">
                    <input
                      type="number"
                      min={0}
                      step={0.01}
                      value={row.rate}
                      onChange={(e) => updateRow(row.id, { rate: parseFloat(e.target.value) || 0 })}
                      className="w-24 rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-right text-white"
                    />
                  </td>
                  <td className="px-3 py-2 text-right">
                    <input
                      type="number"
                      min={0}
                      max={100}
                      step={0.01}
                      value={row.discount_pct}
                      onChange={(e) => updateRow(row.id, { discount_pct: parseFloat(e.target.value) || 0 })}
                      className="w-16 rounded border border-navy-100/30 bg-navy-400 px-2 py-1 text-right text-white"
                    />
                  </td>
                  <td className="px-3 py-2 text-right font-number text-slate-200">{row.taxable.toFixed(2)}</td>
                  <td className="px-3 py-2 text-right">{row.gst_rate}%</td>
                  <td className="px-3 py-2 text-right font-number text-slate-200">{row.cgst + row.sgst}</td>
                  <td className="px-3 py-2 text-right font-number text-gold">{row.total.toFixed(2)}</td>
                  <td className="px-3 py-2">
                    <button type="button" onClick={() => removeRow(row.id)} className="text-slate-500 hover:text-red-400">
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="rounded-xl border border-navy-100/20 bg-navy-400/80 p-4 min-w-[240px]">
          <div className="flex justify-between text-sm"><span className="text-slate-400">Subtotal</span><AmountDisplay amount={subtotal} /></div>
          <div className="flex justify-between text-sm mt-1"><span className="text-slate-400">Tax</span><AmountDisplay amount={totalTax} /></div>
          <div className="flex justify-between font-semibold text-gold mt-2 pt-2 border-t border-navy-100/20">Net Total</div>
          <div className="text-xl font-number text-gold"><AmountDisplay amount={netTotal} /></div>
        </div>
        <div className="flex flex-wrap gap-2">
          <select value={saveAs} onChange={(e) => setSaveAs(e.target.value as "draft" | "final" | "repeat")} className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white">
            <option value="draft">Draft</option>
            <option value="final">Final</option>
            <option value="repeat">Repeat</option>
          </select>
          <button type="button" className="rounded-lg bg-navy-100/30 px-4 py-2 text-slate-200">Save & Print</button>
          <button type="button" className="rounded-lg bg-navy-100/30 px-4 py-2 text-slate-200">Save & WhatsApp</button>
          <button type="button" className="rounded-lg bg-navy-100/30 px-4 py-2 text-slate-200">Save & Email</button>
          <button
            type="button"
            onClick={() => createVoucher.mutate()}
            disabled={createVoucher.isPending || rows.length === 0}
            className="rounded-lg bg-gold px-4 py-2 font-medium text-navy disabled:opacity-50"
          >
            {createVoucher.isPending ? "Saving…" : "Save"}
          </button>
        </div>
      </div>
    </div>
  );
}
