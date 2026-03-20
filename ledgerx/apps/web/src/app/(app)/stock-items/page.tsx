"use client";

import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { stockApi, type StockItem } from "@/lib/api";
import { DataTable } from "@/components/ui/DataTable";
import { AmountDisplay } from "@/components/ui/AmountDisplay";
import { Plus } from "lucide-react";

export default function StockItemsPage() {
  const companyId = useAppStore((s) => s.companyId);
  const { data: items = [] } = useQuery({
    queryKey: ["stock-items", companyId],
    queryFn: () => stockApi.list(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const columns = [
    { key: "name", header: "Name", render: (r: StockItem) => r.name },
    { key: "hsn_code", header: "HSN", render: (r: StockItem) => r.hsn_code ?? "—" },
    { key: "gst_rate", header: "GST %", render: (r: StockItem) => r.gst_rate != null ? `${r.gst_rate}%` : "—" },
    { key: "opening_qty", header: "Stock Qty", render: (r: StockItem) => r.opening_qty },
    { key: "opening_value", header: "Value", render: (r: StockItem) => <AmountDisplay amount={r.opening_value} /> },
    { key: "unit", header: "Unit", render: (r: StockItem) => r.unit ?? "—" },
  ];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Stock Items</h1>
        <button
          type="button"
          className="flex items-center gap-2 rounded-lg bg-gold px-4 py-2 text-sm font-medium text-navy"
        >
          <Plus className="h-4 w-4" /> Add Item
        </button>
      </div>
      <DataTable
        columns={columns}
        data={items}
        keyExtractor={(r) => r.id}
        emptyMessage="No stock items. Add one to get started."
      />
    </div>
  );
}
