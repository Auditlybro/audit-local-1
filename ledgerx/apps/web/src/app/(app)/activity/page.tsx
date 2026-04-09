"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { useAppStore } from "@/lib/store";
import { activityApi, type ActivityLog } from "@/lib/api";
import { format } from "date-fns";
import { 
  History, 
  User, 
  Clock, 
  Filter, 
  ChevronLeft, 
  ChevronRight,
  Database,
  FileUp,
  FileText,
  ShieldCheck,
  Cpu
} from "lucide-react";

const ACTION_ICONS: Record<string, React.ReactNode> = {
  IMPORT: <FileUp className="h-4 w-4" />,
  IMPORT_ROLLBACK: <FileUp className="h-4 w-4 text-red-400" />,
  GST_RETURN: <FileText className="h-4 w-4" />,
  GST_NOTICE_CREATE: <FileText className="h-4 w-4" />,
  AI_ANALYSIS: <Cpu className="h-4 w-4 text-purple-400" />,
  NOTICE_DRAFT: <ShieldCheck className="h-4 w-4 text-emerald-400" />,
  DATA_EDIT: <Database className="h-4 w-4" />,
  USER_LOGIN: <ShieldCheck className="h-4 w-4 text-blue-400" />,
  USER_REGISTER: <User className="h-4 w-4 text-gold" />,
};

const ACTION_COLORS: Record<string, string> = {
  IMPORT: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  IMPORT_ROLLBACK: "bg-red-500/10 text-red-400 border-red-500/20",
  GST_RETURN: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  GST_NOTICE_CREATE: "bg-amber-500/10 text-amber-400 border-amber-500/20",
  AI_ANALYSIS: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  NOTICE_DRAFT: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  DATA_EDIT: "bg-slate-500/10 text-slate-400 border-slate-500/20",
  USER_LOGIN: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  USER_REGISTER: "bg-gold/10 text-gold border-gold/20",
};

export default function ActivityLogPage() {
  const { companyId } = useAppStore();
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const { data, isLoading } = useQuery({
    queryKey: ["activity", companyId, page],
    queryFn: () => activityApi.list(companyId, { page, page_size: pageSize }),
    enabled: true,
  });

  return (
    <div className="p-6 space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3">
            <History className="h-7 w-7 text-gold" />
            Activity Logs
          </h1>
          <p className="text-slate-400 mt-1">Audit trail of all actions performed for this organization.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-navy-100/10 hover:bg-navy-100/20 border border-navy-100/20 rounded-lg text-sm text-slate-300 transition-colors">
            <Filter className="h-4 w-4" />
            Filter
          </button>
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-10 md:left-40 top-0 bottom-0 w-px bg-slate-200/10" />

        <div className="space-y-8">
          {isLoading ? (
            <div className="space-y-8 animate-pulse">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex gap-10 md:gap-20">
                  <div className="hidden md:block w-32 h-4 bg-navy-100/10 rounded mt-2" />
                  <div className="relative">
                    <div className="w-8 h-8 rounded-full bg-navy-100/10" />
                  </div>
                  <div className="flex-1 space-y-2">
                    <div className="w-48 h-5 bg-navy-100/10 rounded" />
                    <div className="w-full h-12 bg-navy-100/10 rounded" />
                  </div>
                </div>
              ))}
            </div>
          ) : !data || data.data.logs.length === 0 ? (
            <div className="py-20 text-center">
              <History className="h-12 w-12 text-slate-600 mx-auto mb-4" />
              <p className="text-slate-400">No activity recorded yet.</p>
            </div>
          ) : (
            data.data.logs.map((log: ActivityLog) => (
              <div key={log.id} className="relative flex flex-col md:flex-row gap-4 md:gap-20 group">
                <div className="hidden md:block w-32 text-right pt-2">
                  <span className="text-xs font-medium text-slate-500 uppercase tracking-wider block">
                    {format(new Date(log.created_at), "hh:mm a")}
                  </span>
                  <span className="text-[10px] text-slate-600 font-mono block mt-0.5">
                    {format(new Date(log.created_at), "MMM d, yyyy")}
                  </span>
                </div>

                <div className="relative z-10 flex md:flex-none justify-center">
                  <div className={`
                    h-10 w-10 md:h-8 md:w-8 rounded-full border flex items-center justify-center shadow-lg transition-transform group-hover:scale-110
                    ${ACTION_COLORS[log.action] || ACTION_COLORS.DATA_EDIT}
                  `}>
                    {ACTION_ICONS[log.action] || <Database className="h-4 w-4" />}
                  </div>
                  <div className="md:hidden ml-4 pt-1">
                    <span className="text-xs font-bold text-slate-300">
                       {format(new Date(log.created_at), "hh:mm a, MMM d")}
                    </span>
                  </div>
                </div>

                <div className="flex-1 bg-navy-100/10 border border-navy-100/10 group-hover:border-gold/20 rounded-xl p-4 transition-all hover:bg-navy-100/20">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <h3 className="font-semibold text-slate-100 group-hover:text-gold transition-colors">
                      {log.description}
                    </h3>
                    <div className="flex items-center gap-3">
                      <div className="flex items-center gap-2 text-xs text-slate-500 bg-black/20 px-2 py-1 rounded">
                        <User className="h-3 w-3" />
                        {log.user_name || "System"}
                      </div>
                      {!log.company_id && (
                        <div className="text-[10px] bg-gold/10 text-gold/80 border border-gold/20 px-1.5 py-0.5 rounded-full uppercase tracking-tighter">
                          All Organizations
                        </div>
                      )}
                    </div>
                  </div>
                  
                  {log.metadata_json && Object.keys(log.metadata_json).length > 0 && (
                    <div className="mt-3 overflow-hidden">
                      <div className="text-[10px] uppercase tracking-widest text-slate-600 mb-1.5 flex items-center gap-2">
                        <Database className="h-2.5 w-2.5" />
                        Metadata
                      </div>
                      <div className="bg-black/40 rounded-lg p-3 font-mono text-[11px] text-slate-400 overflow-x-auto whitespace-pre">
                        {JSON.stringify(log.metadata_json, null, 2)}
                      </div>
                    </div>
                  )}

                  <div className="mt-3 flex items-center gap-4 text-xs text-slate-500 border-t border-navy-100/20 pt-3">
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {format(new Date(log.created_at), "hh:mm:ss a")}
                    </span>
                    <span className="opacity-30">|</span>
                    <span className="uppercase tracking-tighter opacity-70">
                      ID: {log.id.slice(0, 8)}...
                    </span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {data && data.data.total > pageSize && (
        <div className="flex items-center justify-center gap-4 py-8">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="p-2 rounded-lg bg-navy-100/10 hover:bg-navy-100/20 text-slate-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronLeft className="h-5 w-5" />
          </button>
          <span className="text-sm font-medium text-slate-300">
            Page {page} of {Math.ceil(data.data.total / pageSize)}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={page >= Math.ceil(data.data.total / pageSize)}
            className="p-2 rounded-lg bg-navy-100/10 hover:bg-navy-100/20 text-slate-400 disabled:opacity-30 disabled:cursor-not-allowed transition-all"
          >
            <ChevronRight className="h-5 w-5" />
          </button>
        </div>
      )}
    </div>
  );
}
