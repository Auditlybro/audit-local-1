"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { ledgersApi, type Ledger } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { formatINRNoSymbol } from "@/lib/format";
import { Plus, Search } from "lucide-react";

export default function LedgersPage() {
  const companyId = useAppStore((s) => s.companyId);
  const [search, setSearch] = useState("");
  const [groupFilter, setGroupFilter] = useState<string>("");
  const [modalOpen, setModalOpen] = useState(false);

  const { data: ledgers = [] } = useQuery({
    queryKey: ["ledgers", companyId],
    queryFn: () => ledgersApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });
  const { data: groups = [] } = useQuery({
    queryKey: ["ledger-groups", companyId],
    queryFn: () => ledgersApi.listGroups(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const filtered = ledgers.filter((l) => {
    const matchSearch = !search || l.name.toLowerCase().includes(search.toLowerCase()) || (l.alias?.toLowerCase().includes(search.toLowerCase()));
    const matchGroup = !groupFilter || l.group_id === groupFilter;
    return matchSearch && matchGroup;
  });

  const columns = [
    { key: "name", header: "Name", render: (r: Ledger) => r.name },
    { key: "group", header: "Group", render: (r: Ledger) => groups.find((g) => g.id === r.group_id)?.name ?? "—" },
    { key: "balance", header: "Balance (Dr/Cr)", render: (r: Ledger) => (r.opening_balance >= 0 ? "Dr " : "Cr ") + formatINRNoSymbol(Math.abs(r.opening_balance)) },
  ];

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-white">Ledgers</h1>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="flex items-center gap-2 rounded-lg bg-gold px-4 py-2 text-sm font-medium text-navy"
        >
          <Plus className="h-4 w-4" /> Add Ledger
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-500" />
          <input
            type="text"
            placeholder="Search by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-64 rounded-lg border border-navy-100/30 bg-navy-400 pl-9 pr-3 py-2 text-white placeholder-slate-500"
          />
        </div>
        <select
          value={groupFilter}
          onChange={(e) => setGroupFilter(e.target.value)}
          className="rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white"
        >
          <option value="">All groups</option>
          {groups.map((g) => (
            <option key={g.id} value={g.id}>{g.name}</option>
          ))}
        </select>
      </div>
      <DataTable
        columns={columns}
        data={filtered}
        keyExtractor={(r) => r.id}
        emptyMessage="No ledgers. Add one to get started."
      />
      {modalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
          <div className="w-full max-w-md rounded-xl border border-navy-100/20 bg-navy-400 p-6">
            <h2 className="text-lg font-semibold text-white">Add Ledger (placeholder)</h2>
            <p className="mt-2 text-sm text-slate-400">Connect to ledgersApi.create with form fields.</p>
            <button type="button" onClick={() => setModalOpen(false)} className="mt-4 rounded-lg bg-navy-100/30 px-4 py-2 text-sm text-slate-200">Close</button>
          </div>
        </div>
      )}
    </div>
  );
}
