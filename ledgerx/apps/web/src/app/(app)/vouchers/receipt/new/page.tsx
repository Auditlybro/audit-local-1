"use client";

import Link from "next/link";

export default function NewReceiptPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">New Receipt</h1>
      <p className="text-slate-500 dark:text-slate-400">Same as Payment, flipped (Debtor + amount received). See <Link href="/vouchers/payment/new" className="text-gold hover:underline">Payment form</Link> with voucher_type RECEIPT.</p>
    </div>
  );
}
