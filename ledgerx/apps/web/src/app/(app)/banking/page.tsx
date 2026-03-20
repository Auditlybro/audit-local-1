"use client";

import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { bankingApi } from "@/lib/api";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import Link from "next/link";
import { Landmark } from "lucide-react";

export default function BankingPage() {
  const companyId = useAppStore((s) => s.companyId);
  const { data: accounts = [] } = useQuery({
    queryKey: ["bank-accounts", companyId],
    queryFn: () => bankingApi.listAccounts(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Bank Accounts</h1>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {(accounts as { id: string; account_number: string; bank_name: string | null; opening_balance: number }[]).map((acc) => (
          <Link key={acc.id} href={`/banking/${acc.id}`} className="rounded-xl border border-navy-100/20 bg-navy-400/80 p-4 hover:border-gold/30">
            <Landmark className="h-8 w-8 text-gold mb-2" />
            <p className="font-medium text-white">{acc.bank_name ?? "Bank"}</p>
            <p className="text-sm text-slate-400">A/c {acc.account_number}</p>
            <p className="mt-2 font-number text-gold"><AmountDisplay amount={acc.opening_balance} /></p>
          </Link>
        ))}
      </div>
      {accounts.length === 0 && <p className="text-slate-500">No bank accounts. Add from ledgers (link ledger to bank).</p>}
    </div>
  );
}
