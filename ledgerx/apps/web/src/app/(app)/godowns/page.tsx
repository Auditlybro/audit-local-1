"use client";

import { useAppStore } from "@/lib/store";
import { Warehouse } from "lucide-react";

export default function GodownsPage() {
  useAppStore((s) => s.companyId);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-white">Godowns</h1>
      <p className="text-slate-400 text-sm">Godown list + stock per godown. Connect to godowns API when available.</p>
      <div className="rounded-xl border border-navy-100/20 bg-navy-400/80 p-8 text-center text-slate-500">
        <Warehouse className="mx-auto h-12 w-12 text-slate-600" />
        <p className="mt-2">No godowns yet. Add from masters when API is ready.</p>
      </div>
    </div>
  );
}
