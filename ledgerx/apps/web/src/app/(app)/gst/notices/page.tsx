"use client";

import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { gstApi } from "@/lib/api";
import { Plus } from "lucide-react";

export default function GstNoticesPage() {
  const companyId = useAppStore((s) => s.companyId);
  const { data: notices = [] } = useQuery({
    queryKey: ["gst-notices", companyId],
    queryFn: () => gstApi.notices(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">GST Notices</h1>
        <button type="button" className="flex items-center gap-2 rounded-lg bg-gold px-4 py-2 text-navy"><Plus className="h-4 w-4" /> Add notice</button>
      </div>
      <p className="text-slate-400">Notice list + status. Add notice → auto-analyze → draft reply (Audit-Local Notice Doctor).</p>
      <div className="rounded-xl border border-navy-100/20 overflow-hidden">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-navy-100/20 bg-navy-100/20"><th className="px-4 py-3 text-left text-slate-400">Ref</th><th className="px-4 py-3 text-left text-slate-400">Type</th><th className="px-4 py-3 text-left text-slate-400">Status</th></tr></thead>
          <tbody>
            {(notices as { notice_ref?: string; notice_type?: string; status?: string }[]).map((n, i) => (
              <tr key={i} className="border-b border-navy-100/10"><td className="px-4 py-2 text-slate-200">{n.notice_ref ?? "—"}</td><td className="px-4 py-2 text-slate-200">{n.notice_type ?? "—"}</td><td className="px-4 py-2 text-slate-200">{n.status ?? "—"}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
