"use client";

import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import {
  Receipt,
  Wallet,
  Users,
  FileCheck,
  TrendingUp,
  BarChart3,
  Plus,
} from "lucide-react";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { vouchersApi } from "@/lib/api";

const statCards = [
  { title: "Today's Sales", value: 0, icon: Receipt, color: "text-gold" },
  { title: "Cash Balance", value: 0, icon: Wallet, color: "text-emerald-400" },
  { title: "Outstanding Receivable", value: 0, icon: Users, color: "text-blue-400" },
  { title: "GST Due", value: 0, icon: FileCheck, color: "text-amber-400" },
];

const quickActions = [
  { href: "/vouchers/sales/new", label: "New Sale", icon: Receipt },
  { href: "/vouchers/purchase/new", label: "New Purchase", icon: Receipt },
  { href: "/vouchers/receipt/new", label: "New Receipt", icon: Plus },
  { href: "/vouchers/payment/new", label: "New Payment", icon: Plus },
];

export default function DashboardPage() {
  const companyId = useAppStore((s) => s.companyId);

  const { data: vouchers } = useQuery({
    queryKey: ["vouchers", companyId],
    queryFn: () => vouchersApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Dashboard</h1>
        <p className="mt-1 text-slate-500 dark:text-slate-400">Overview of your business</p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((card) => {
          const Icon = card.icon;
          return (
            <div
              key={card.title}
              className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4"
            >
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-500 dark:text-slate-400">{card.title}</span>
                <Icon className={`h-5 w-5 ${card.color}`} />
              </div>
              <p className="mt-2 text-xl font-semibold font-number text-slate-900 dark:text-white">
                <AmountDisplay amount={card.value} />
              </p>
            </div>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-gold" />
            Sales vs Purchase (last 6 months)
          </h2>
          <div className="mt-4 h-64 flex items-center justify-center text-slate-500 text-sm">
            Chart placeholder — connect reports API
          </div>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-slate-900 dark:text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-gold" />
            Cash flow trend
          </h2>
          <div className="mt-4 h-64 flex items-center justify-center text-slate-500 text-sm">
            Line chart placeholder
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-4">
        {quickActions.map((a) => {
          const Icon = a.icon;
          return (
            <Link
              key={a.href}
              href={a.href}
              className="flex items-center gap-2 rounded-lg border border-gold/50 bg-gold/10 px-4 py-2 text-gold hover:bg-gold/20"
            >
              <Icon className="h-4 w-4" />
              {a.label}
            </Link>
          );
        })}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-slate-900 dark:text-white">Recent vouchers</h2>
          <ul className="mt-3 space-y-2">
            {(vouchers as { id: string; number: string; voucher_type: string; date: string; amount: number }[] | undefined)?.slice(0, 5).map((v) => (
              <li
                key={v.id}
                className="flex justify-between text-sm text-slate-600 dark:text-slate-300"
              >
                <span>{v.number || v.voucher_type} — {v.date}</span>
                <AmountDisplay amount={v.amount} className="text-slate-200" />
              </li>
            )) ?? (
              <li className="text-sm text-slate-500">No vouchers yet</li>
            )}
          </ul>
          <Link href="/vouchers" className="mt-2 inline-block text-sm text-gold hover:underline">
            View all →
          </Link>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-slate-900 dark:text-white">Top 5 debtors</h2>
          <p className="mt-3 text-sm text-slate-500">— Connect outstanding API</p>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-slate-900 dark:text-white">GST filing deadlines</h2>
          <p className="mt-3 text-sm text-slate-500">— Connect GST dashboard API</p>
        </div>
        <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
          <h2 className="font-semibold text-slate-900 dark:text-white">Low stock alerts</h2>
          <p className="mt-3 text-sm text-slate-500">— Connect stock summary API</p>
        </div>
      </div>
    </div>
  );
}
