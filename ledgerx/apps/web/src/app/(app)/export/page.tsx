"use client";

import { useState } from "react";
import { useAppStore } from "@/lib/store";
import { FileCode, FileSpreadsheet, FileText } from "lucide-react";

export default function ExportPage() {
  useAppStore((s) => s.companyId);
  const [reportType, setReportType] = useState("trial-balance");
  const [fromDate, setFromDate] = useState("");
  const [toDate, setToDate] = useState("");
  const [format, setFormat] = useState<"excel" | "pdf" | "tally">("excel");

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white">Export</h1>
      <p className="text-slate-400">Choose report type, date range, and format. One-click export.</p>
      <div className="rounded-xl border border-navy-100/20 bg-navy-400/80 p-6 max-w-lg space-y-4">
        <div>
          <label className="block text-sm text-slate-400">Report type</label>
          <select value={reportType} onChange={(e) => setReportType(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white">
            <option value="trial-balance">Trial Balance</option>
            <option value="balance-sheet">Balance Sheet</option>
            <option value="profit-loss">Profit & Loss</option>
            <option value="sales-register">Sales Register</option>
            <option value="gst-json">GST JSON</option>
          </select>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-slate-400">From</label>
            <input type="date" value={fromDate} onChange={(e) => setFromDate(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white" />
          </div>
          <div>
            <label className="block text-sm text-slate-400">To</label>
            <input type="date" value={toDate} onChange={(e) => setToDate(e.target.value)} className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-400 px-3 py-2 text-white" />
          </div>
        </div>
        <div>
          <label className="block text-sm text-slate-400">Format</label>
          <div className="flex gap-2 mt-2">
            <button type="button" onClick={() => setFormat("excel")} className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm ${format === "excel" ? "bg-gold text-navy" : "bg-navy-100/30 text-slate-400"}`}><FileSpreadsheet className="h-4 w-4" /> Excel</button>
            <button type="button" onClick={() => setFormat("pdf")} className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm ${format === "pdf" ? "bg-gold text-navy" : "bg-navy-100/30 text-slate-400"}`}><FileText className="h-4 w-4" /> PDF</button>
            <button type="button" onClick={() => setFormat("tally")} className={`flex items-center gap-2 rounded-lg px-4 py-2 text-sm ${format === "tally" ? "bg-gold text-navy" : "bg-navy-100/30 text-slate-400"}`}><FileCode className="h-4 w-4" /> Tally XML</button>
          </div>
        </div>
        <button type="button" className="w-full rounded-lg bg-gold py-2.5 font-medium text-navy">Export</button>
      </div>
    </div>
  );
}
