"use client";

import { format } from "date-fns";
import { Download, FileSpreadsheet, Printer } from "lucide-react";
import { cn } from "@/lib/cn";

type ReportWrapperProps = {
  title: string;
  children: React.ReactNode;
  onExportExcel?: () => void;
  onExportPdf?: () => void;
  onPrint?: () => void;
  fromDate?: Date;
  toDate?: Date;
  onFromChange?: (d: Date) => void;
  onToChange?: (d: Date) => void;
  singleDate?: Date;
  onSingleDateChange?: (d: Date) => void;
  mode?: "range" | "single";
  className?: string;
};

export function ReportWrapper({
  title,
  children,
  onExportExcel,
  onExportPdf,
  onPrint,
  fromDate = new Date(new Date().getFullYear(), 3, 1),
  toDate = new Date(),
  onFromChange,
  onToChange,
  singleDate = new Date(),
  onSingleDateChange,
  mode = "range",
  className,
}: ReportWrapperProps) {
  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h1 className="text-xl font-semibold text-slate-900 dark:text-white">{title}</h1>
        <div className="flex flex-wrap items-center gap-2">
          {mode === "range" && onFromChange && onToChange && (
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={format(fromDate, "yyyy-MM-dd")}
                onChange={(e) => onFromChange(new Date(e.target.value))}
                className="rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-sm text-slate-900 dark:text-white"
              />
              <span className="text-slate-500 dark:text-slate-400">to</span>
              <input
                type="date"
                value={format(toDate, "yyyy-MM-dd")}
                onChange={(e) => onToChange(new Date(e.target.value))}
                className="rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-sm text-slate-900 dark:text-white"
              />
            </div>
          )}
          {mode === "single" && onSingleDateChange && (
            <input
              type="date"
              value={format(singleDate, "yyyy-MM-dd")}
              onChange={(e) => onSingleDateChange(new Date(e.target.value))}
              className="rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-sm text-slate-900 dark:text-white"
            />
          )}
          {onExportExcel && (
            <button
              type="button"
              onClick={onExportExcel}
              className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-sm text-slate-200 hover:bg-slate-100 dark:bg-navy-100/30"
            >
              <FileSpreadsheet className="w-4 h-4" /> Excel
            </button>
          )}
          {onExportPdf && (
            <button
              type="button"
              onClick={onExportPdf}
              className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-sm text-slate-200 hover:bg-slate-100 dark:bg-navy-100/30"
            >
              <Download className="w-4 h-4" /> PDF
            </button>
          )}
          {onPrint && (
            <button
              type="button"
              onClick={onPrint}
              className="flex items-center gap-2 rounded-lg border border-slate-200 dark:border-navy-100/30 bg-white dark:bg-navy-400 px-3 py-2 text-sm text-slate-200 hover:bg-slate-100 dark:bg-navy-100/30"
            >
              <Printer className="w-4 h-4" /> Print
            </button>
          )}
        </div>
      </div>
      {children}
    </div>
  );
}
