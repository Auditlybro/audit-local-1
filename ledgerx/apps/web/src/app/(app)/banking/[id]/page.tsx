"use client";

import { useParams } from "next/navigation";
import { useAppStore } from "@/lib/store";

export default function BankingReconcilePage() {
  useParams();
  useAppStore((s) => s.companyId);

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Bank Ledger & Reconciliation</h1>
      <p className="text-slate-500 dark:text-slate-400">Left: Our books. Right: Bank statement. Auto-match (green), manual match, BRS summary. Connect to banking API.</p>
      <div className="grid md:grid-cols-2 gap-6">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-gold mb-2">Our books</h2>
          <p className="text-slate-500 text-sm">Transactions from vouchers</p>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-gold mb-2">Bank statement</h2>
          <p className="text-slate-500 text-sm">Imported statement lines</p>
        </div>
      </div>
    </div>
  );
}
