"use client";

import { useAppStore } from "@/lib/store";
import { useQuery } from "@tanstack/react-query";
import { ledgersApi, type LedgerGroup } from "@/lib/api";
import { ChevronRight, Folder } from "lucide-react";
import { useState } from "react";

function GroupRow({ g, groups, level = 0 }: { g: LedgerGroup; groups: LedgerGroup[]; level?: number }) {
  const [open, setOpen] = useState(true);
  const children = groups.filter((c) => c.parent_id === g.id);
  const hasChildren = children.length > 0;

  return (
    <div className="select-none">
      <div
        style={{ paddingLeft: level * 20 }}
        className="flex items-center gap-2 py-2 px-2 rounded hover:bg-slate-100 dark:bg-navy-100/20"
      >
        <button type="button" onClick={() => setOpen((o) => !o)} className="p-0.5">
          {hasChildren ? (
            <ChevronRight className={`h-4 w-4 text-slate-500 dark:text-slate-400 transition-transform ${open ? "rotate-90" : ""}`} />
          ) : (
            <span className="w-4 inline-block" />
          )}
        </button>
        <Folder className="h-4 w-4 text-gold" />
        <span className="text-slate-200">{g.name}</span>
        <span className="text-xs text-slate-500">({g.nature})</span>
      </div>
      {open && hasChildren && (
        <div>
          {children.map((c) => (
            <GroupRow key={c.id} g={c} groups={groups} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
}

export default function LedgerGroupsPage() {
  const companyId = useAppStore((s) => s.companyId);
  const { data: groups = [] } = useQuery({
    queryKey: ["ledger-groups", companyId],
    queryFn: () => ledgersApi.listGroups(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });
  const roots = groups.filter((g) => !g.parent_id);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Ledger Groups</h1>
      <p className="text-slate-500 dark:text-slate-400 text-sm">28 Tally-compatible groups + custom. Tree view.</p>
      <div className="rounded-xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-4">
        {roots.map((g) => (
          <GroupRow key={g.id} g={g} groups={groups} />
        ))}
      </div>
    </div>
  );
}
