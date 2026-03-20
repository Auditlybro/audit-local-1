"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ledgersApi, vouchersApi } from "@/lib/api";
import { format } from "date-fns";

export default function NewPaymentPage() {
  const companyId = useAppStore((s) => s.companyId);
  const queryClient = useQueryClient();
  const [partyId, setPartyId] = useState("");
  const [date, setDate] = useState(format(new Date(), "yyyy-MM-dd"));
  const [amount, setAmount] = useState(0);
  const [mode, setMode] = useState<"Cash" | "Bank" | "UPI">("Cash");
  const [bankLedgerId, setBankLedgerId] = useState("");
  const [billRef, setBillRef] = useState("");

  const { data: ledgers = [] } = useQuery({
    queryKey: ["ledgers", companyId],
    queryFn: () => ledgersApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const createPayment = useMutation({
    mutationFn: () =>
      vouchersApi.create(companyId!, {
        voucher_type: "PAYMENT",
        date,
        party_ledger_id: partyId,
        entries: [
          { ledger_id: partyId, dr_amount: amount, cr_amount: 0 },
          { ledger_id: mode === "Cash" ? (ledgers.find((l) => l.name.toLowerCase().includes("cash"))?.id ?? "") : bankLedgerId, dr_amount: 0, cr_amount: amount, bill_ref: billRef || undefined },
        ].filter((e) => e.ledger_id),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["vouchers", companyId] });
      window.history.back();
    },
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="text-2xl font-bold text-white">New Payment</h1>
      <div className="space-y-4 rounded-xl border border-navy-100/20 bg-navy-400/80 p-6">
        <div>
          <label className="block text-sm text-slate-400">Party (Creditor)</label>
          <select
            value={partyId}
            onChange={(e) => setPartyId(e.target.value)}
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
          >
            <option value="">Select party</option>
            {ledgers.map((l) => (
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
        <div>
          <label className="block text-sm text-slate-400">Amount (₹)</label>
          <input
            type="number"
            min={0}
            step={0.01}
            value={amount || ""}
            onChange={(e) => setAmount(parseFloat(e.target.value) || 0)}
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white font-number"
          />
        </div>
        <div>
          <label className="block text-sm text-slate-400">Payment mode</label>
          <select
            value={mode}
            onChange={(e) => setMode(e.target.value as "Cash" | "Bank" | "UPI")}
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
          >
            <option value="Cash">Cash</option>
            <option value="Bank">Bank</option>
            <option value="UPI">UPI</option>
          </select>
        </div>
        {mode === "Bank" && (
          <div>
            <label className="block text-sm text-slate-400">Bank ledger</label>
            <select
              value={bankLedgerId}
              onChange={(e) => setBankLedgerId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
            >
              <option value="">Select bank</option>
              {ledgers.filter((l) => l.name.toLowerCase().includes("bank")).map((l) => (
                <option key={l.id} value={l.id}>{l.name}</option>
              ))}
            </select>
          </div>
        )}
        <div>
          <label className="block text-sm text-slate-400">Against bill reference (optional)</label>
          <input
            type="text"
            value={billRef}
            onChange={(e) => setBillRef(e.target.value)}
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
          />
        </div>
        <button
          type="button"
          onClick={() => createPayment.mutate()}
          disabled={createPayment.isPending || !partyId || amount <= 0}
          className="rounded-lg bg-gold px-4 py-2 font-medium text-navy disabled:opacity-50"
        >
          {createPayment.isPending ? "Saving…" : "Save Payment"}
        </button>
      </div>
    </div>
  );
}
