"use client";

import Link from "next/link";

export default function NewPurchasePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">New Purchase</h1>
      <p className="text-slate-500 dark:text-slate-400">Same form as Sales, flipped (purchase party + items). Use the same structure as <Link href="/vouchers/sales/new" className="text-gold hover:underline">/vouchers/sales/new</Link> with voucher_type PURCHASE.</p>
    </div>
  );
}
