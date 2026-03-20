"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ledgersApi, vouchersApi } from "@/lib/api";
import { format } from "date-fns";

export default function NewContraPage() {
  const companyId = useAppStore((s) => s.companyId);
  const queryClient = useQueryClient();
  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [amount, setAmount] = useState(0);
  const [type, setType] = useState<"CashToBank" | "BankToCash">("CashToBank");
  const [cashLedgerId, setCashLedgerId] = useState("");
  const [bankLedgerId, setBankLedgerId] = useState("");

  const { data: ledgers = [] } = useQuery({
    queryKey: ["ledgers", companyId],
    queryFn: () => ledgersApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });
  const cashLedgers = ledgers.filter((l) => l.name.toLowerCase().includes("cash"));
  const bankLedgers = ledgers.filter((l) => l.name.toLowerCase().includes("bank"));

  const createContra = useMutation({
    mutationFn: () => {
      return vouchersApi.create(companyId!, {
        voucher_type: "CONTRA",
        date,
        entries: [
          { ledger_id: type === "CashToBank" ? bankLedgerId : cashLedgerId, dr_amount: amount, cr_amount: 0 },
          { ledger_id: type === "CashToBank" ? cashLedgerId : bankLedgerId, dr_amount: 0, cr_amount: amount },
        ].filter((e) => e.ledger_id),
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vouchers", companyId] });
      window.history.back();
    },
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-white">Contra (Cash ⇄ Bank)</h1>
      <div className="space-y-4 rounded-xl border border-navy-100/20 bg-navy-400/80 p-6">
        <div>
          <label className="block text-sm text-slate-400">Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white" />
        </div>
        <div>
          <label className="block text-sm text-slate-400">Transfer</label>
          <select value={type} onChange={(e) => setType(e.target.value as "CashToBank" | "BankToCash")} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white">
            <option value="CashToBank">Cash to Bank</option>
            <option value="BankToCash">Bank to Cash</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400">Amount (₹)</label>
          <input type="number" min={0} step={0.01} value={amount || ""} onChange={(e) => setAmount(parseFloat(e.target.value) || 0)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white font-number" />
        </div>
        <div>
          <label className="block text-sm text-slate-400">Cash ledger</label>
          <select value={cashLedgerId} onChange={(e) => setCashLedgerId(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white">
            <option value="">Select</option>
            {cashLedgers.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm text-slate-400">Bank ledger</label>
          <select value={bankLedgerId} onChange={(e) => setBankLedgerId(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white">
            <option value="">Select</option>
            {bankLedgers.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        </div>
        <button type="button" onClick={() => createContra.mutate()} disabled={createContra.isPending || !amount || !cashLedgerId || !bankLedgerId} className="rounded-lg bg-gold px-4 py-2 font-medium text-navy disabled:opacity-50">
          {createContra.isPending ? "Saving…" : "Save Contra"}
        </button>
      </div>
    </div>
  );
}
