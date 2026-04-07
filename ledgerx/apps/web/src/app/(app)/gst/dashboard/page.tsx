"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import clsx from "clsx";
import { format, parseISO } from "date-fns";
import { AlertTriangle, Calendar, CheckCircle2, Clock } from "lucide-react";
import { useAppStore } from "@/lib/store";
import { gstApi, type GstCalendarItem } from "@/lib/api";

function statusStyles(status: GstCalendarItem["status"]) {
  switch (status) {
    case "red":
      return {
        ring: "border-red-500/45 bg-red-950/30",
        badge: "bg-red-500/20 text-red-200",
        label: "Overdue / critical",
      };
    case "amber":
      return {
        ring: "border-amber-500/45 bg-amber-950/25",
        badge: "bg-amber-500/20 text-amber-100",
        label: "Due within 7 days",
      };
    default:
      return {
        ring: "border-emerald-500/35 bg-emerald-950/20",
        badge: "bg-emerald-500/15 text-emerald-100",
        label: "Filed / on track",
      };
  }
}

function DeadlineCard({
  item,
  onMarkFiled,
  pending,
}: {
  item: GstCalendarItem;
  onMarkFiled: () => void;
  pending: boolean;
}) {
  const s = statusStyles(item.status);
  return (
    <div className={clsx("rounded-xl border p-4", s.ring)}>
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <p className="font-medium text-white">{item.title}</p>
          <p className="mt-1 text-sm text-slate-400">{item.description}</p>
          <p className="mt-2 text-sm text-slate-300">
            Due{" "}
            <span className="font-mono text-gold">
              {format(parseISO(item.due_date), "dd MMM yyyy")}
            </span>
            <span className="text-slate-500"> · {item.return_type}</span>
            <span className="text-slate-600"> · {item.period}</span>
          </p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className={clsx("rounded-full px-2.5 py-0.5 text-xs font-medium", s.badge)}>{s.label}</span>
          {!item.filed && (
            <button
              type="button"
              disabled={pending}
              onClick={onMarkFiled}
              className="rounded-lg border border-navy-100/30 bg-navy-100/20 px-3 py-1.5 text-xs font-medium text-slate-200 hover:bg-navy-100/40 disabled:opacity-50"
            >
              Mark filed
            </button>
          )}
          {item.filed && (
            <span className="flex items-center gap-1 text-xs text-emerald-400">
              <CheckCircle2 className="h-3.5 w-3.5" /> Filed
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function SectionBlock({
  title,
  subtitle,
  rangeLabel,
  items,
  companyId,
  isLoading,
}: {
  title: string;
  subtitle: string;
  rangeLabel: string;
  items: GstCalendarItem[];
  companyId: string | null;
  isLoading: boolean;
}) {
  const queryClient = useQueryClient();
  const markMutation = useMutation({
    mutationFn: ({ return_type, period }: { return_type: string; period: string }) =>
      gstApi.markFiled(companyId!, { return_type, period }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["gst-compliance", companyId] });
    },
  });

  return (
    <section className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-white">{title}</h2>
        <p className="text-sm text-slate-500">{subtitle}</p>
        <p className="mt-1 text-xs font-mono text-slate-600">{rangeLabel}</p>
      </div>
      {!companyId && <p className="text-sm text-slate-500">Select a company to load deadlines.</p>}
      {companyId && isLoading && <p className="text-slate-400">Loading…</p>}
      {companyId && !isLoading && items.length === 0 && (
        <p className="rounded-lg border border-navy-100/15 bg-navy-400/40 px-4 py-6 text-center text-sm text-slate-500">
          No statutory dues in this range (or all caught up).
        </p>
      )}
      <div className="space-y-3">
        {items.map((item) => (
          <DeadlineCard
            key={`${item.return_type}-${item.period}-${item.due_date}`}
            item={item}
            pending={markMutation.isPending}
            onMarkFiled={() => markMutation.mutate({ return_type: item.return_type, period: item.period })}
          />
        ))}
      </div>
    </section>
  );
}

export default function GstDashboardPage() {
  const companyId = useAppStore((s) => s.companyId);

  const { data: summary, isLoading } = useQuery({
    queryKey: ["gst-compliance", companyId],
    queryFn: () => gstApi.complianceSummary(companyId!).then((r) => r.data),
    enabled: !!companyId,
  });

  const weekRange = summary
    ? `${format(parseISO(summary.this_week.start), "dd MMM")} – ${format(parseISO(summary.this_week.end), "dd MMM yyyy")}`
    : "";
  const monthRange = summary
    ? `${format(parseISO(summary.this_month.start), "dd MMM")} – ${format(parseISO(summary.this_month.end), "dd MMM yyyy")}`
    : "";

  return (
    <div className="space-y-10">
      <div>
        <h1 className="text-2xl font-bold text-white">GST calendar & deadlines</h1>
        <p className="mt-2 max-w-3xl text-slate-400">
          Indian GST due dates (GSTR-1, GSTR-3B, GSTR-9, advance tax) are computed from statutory rules. Mark returns as filed
          to track compliance; daily Celery reminders log pending items (wire email/WhatsApp in production).
        </p>
        <div className="mt-4 flex flex-wrap gap-4 text-sm text-slate-500">
          <span className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-gold" /> Week & month views
          </span>
          <span className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-amber-400" /> Amber = due in 7 days
          </span>
          <span className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-red-400" /> Red = overdue
          </span>
          <span className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" /> Green = filed or not urgent
          </span>
        </div>
      </div>

      <div className="grid gap-10 lg:grid-cols-2">
        <SectionBlock
          title="This week"
          subtitle="Returns due Monday–Sunday (current week)"
          rangeLabel={weekRange}
          items={summary?.this_week.items ?? []}
          companyId={companyId}
          isLoading={isLoading}
        />
        <SectionBlock
          title="This month"
          subtitle="All obligations due in the current calendar month"
          rangeLabel={monthRange}
          items={summary?.this_month.items ?? []}
          companyId={companyId}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
}
