"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { vouchersApi, type Voucher } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { formatDateDisplay } from "@/lib/format";
import Link from "next/link";
import { Eye, Pencil, Printer, MessageCircle } from "lucide-react";

export default function VouchersListPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [typeFilter, setTypeFilter] = useState("");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [search, setSearch] = useState("");

  const { data: vouchers = [] } = useQuery({
    queryKey: ["vouchers", companyId, typeFilter, fromDate, toDate],
    queryFn: () =>
      vouchersApi.list(companyId!, {
        voucher_type: typeFilter || undefined,
        from: fromDate || undefined,
        to: toDate || undefined,
      }).then((r) => r.data),
    enabled: !!companyId,
  });

  const filtered = vouchers.filter((v) => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      (v.number?.toLowerCase().includes(s)) ||
      (v.narration?.toLowerCase().includes(s))
    );
  });

  const columns = [
    { key: "number", header: "Number", render: (r: Voucher) => r.number ?? r.id.slice(0, 8) },
    { key: "type", header: "Type", render: (r: Voucher) => r.voucher_type },
    { key: "date", header: "Date", render: (r: Voucher) => formatDateDisplay(r.date) },
    { key: "amount", header: "Amount", render: (r: Voucher) => <AmountDisplay amount={r.amount} /> },
    { key: "narration", header: "Narration", render: (r: Voucher) => (r.narration?.slice(0, 40) ?? "—") + (r.narration && r.narration.length > 40 ? "…" : "") },
    {
      key: "actions",
      header: "Actions",
      render: (r: Voucher) => (
        <div className="flex gap-2">
          <Link href={`/vouchers/${r.id}`} className="text-slate-400 hover:text-gold" title="View"><Eye className="h-4 w-4" /></Link>
          <button type="button" className="text-slate-400 hover:text-gold" title="Edit"><Pencil className="h-4 w-4" /></button>
          <button type="button" className="text-slate-400 hover:text-gold" title="Print"><Printer className="h-4 w-4" /></button>
          <button type="button" className="text-slate-400 hover:text-gold" title="WhatsApp"><MessageCircle className="h-4 w-4" /></button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white">All Vouchers</h1>
      <div className="flex flex-wrap gap-2">
        <input
          type="date"
          value={fromDate}
          onChange={(e) => setFromDate(e.target.value)}
          className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
        />
        <input
          type="date"
          value={toDate}
          onChange={(e) => setToDate(e.target.value)}
          className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
        />
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
        >
          <option value="">All types</option>
          <option value="SALES">Sales</option>
          <option value="PURCHASE">Purchase</option>
          <option value="PAYMENT">Payment</option>
          <option value="RECEIPT">Receipt</option>
          <option value="JOURNAL">Journal</option>
          <option value="CONTRA">Contra</option>
        </select>
        <input
          type="text"
          placeholder="Search number, narration..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white placeholder-slate-500 w-56"
        />
      </div>
      <DataTable
        columns={columns}
        data={filtered}
        keyExtractor={(r) => r.id}
        emptyMessage="No vouchers in this range."
      />
    </div>
  );
}
