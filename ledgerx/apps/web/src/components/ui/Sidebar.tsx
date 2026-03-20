"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import clsx from "clsx";
import {
  LayoutDashboard,
  BookOpen,
  FolderTree,
  Package,
  Warehouse,
  FileText,
  Receipt,
  BarChart3,
  FileSpreadsheet,
  Landmark,
  Download,
  Upload,
  Users,
  ChevronDown,
  ChevronRight,
} from "lucide-react";

const navSections = [
  {
    title: "Main",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
    ],
  },
  {
    title: "Masters",
    items: [
      { href: "/ledgers", label: "Ledgers", icon: BookOpen },
      { href: "/ledger-groups", label: "Ledger Groups", icon: FolderTree },
      { href: "/stock-items", label: "Stock Items", icon: Package },
      { href: "/godowns", label: "Godowns", icon: Warehouse },
    ],
  },
  {
    title: "Vouchers",
    items: [
      { href: "/vouchers", label: "All Vouchers", icon: FileText },
      { href: "/vouchers/sales/new", label: "New Sale", icon: Receipt },
      { href: "/vouchers/purchase/new", label: "New Purchase", icon: Receipt },
      { href: "/vouchers/payment/new", label: "New Payment", icon: Receipt },
      { href: "/vouchers/receipt/new", label: "New Receipt", icon: Receipt },
      { href: "/vouchers/journal/new", label: "Journal", icon: FileText },
      { href: "/vouchers/contra/new", label: "Contra", icon: FileText },
    ],
  },
  {
    title: "Reports",
    items: [
      { href: "/reports/trial-balance", label: "Trial Balance", icon: BarChart3 },
      { href: "/reports/balance-sheet", label: "Balance Sheet", icon: FileSpreadsheet },
      { href: "/reports/profit-loss", label: "Profit & Loss", icon: BarChart3 },
      { href: "/reports/outstanding", label: "Outstanding", icon: BarChart3 },
      { href: "/reports/sales-register", label: "Sales Register", icon: FileText },
      { href: "/reports/stock-summary", label: "Stock Summary", icon: Package },
    ],
  },
  {
    title: "GST & Banking",
    items: [
      { href: "/gst/dashboard", label: "GST Dashboard", icon: FileSpreadsheet },
      { href: "/gst/gstr1", label: "GSTR-1", icon: FileText },
      { href: "/gst/gstr3b", label: "GSTR-3B", icon: FileText },
      { href: "/gst/reconciliation", label: "Reconciliation", icon: BarChart3 },
      { href: "/gst/notices", label: "Notices", icon: FileText },
      { href: "/banking", label: "Banking", icon: Landmark },
    ],
  },
  {
    title: "Data",
    items: [
      { href: "/import", label: "Import", icon: Upload },
      { href: "/export", label: "Export", icon: Download },
    ],
  },
  {
    title: "CA Portal",
    items: [
      { href: "/ca/clients", label: "Clients", icon: Users },
      { href: "/ca/tasks", label: "Tasks", icon: FileText },
      { href: "/ca/notices", label: "Notices", icon: FileText },
      { href: "/ca/reports", label: "Reports", icon: BarChart3 },
    ],
  },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);
  const [openSections, setOpenSections] = useState<Record<string, boolean>>({});

  const toggleSection = (title: string) => {
    setOpenSections((p) => ({ ...p, [title]: !p[title] }));
  };

  return (
    <aside
      className={clsx(
        "flex flex-col bg-navy-400 border-r border-navy-100/20 text-slate-200 transition-all duration-200",
        collapsed ? "w-[72px]" : "w-64"
      )}
    >
      <div className="flex h-14 items-center justify-between px-3 border-b border-navy-100/20">
        {!collapsed && (
          <Link href="/dashboard" className="font-semibold text-gold flex items-center gap-2">
            <span className="text-xl">L</span> LedgerX
          </Link>
        )}
        <button
          type="button"
          onClick={() => setCollapsed((c) => !c)}
          className="p-2 rounded hover:bg-navy-100/30 text-slate-400"
          aria-label={collapsed ? "Expand" : "Collapse"}
        >
          {collapsed ? <ChevronRight className="w-5 h-5" /> : <ChevronDown className="w-5 h-5 rotate-[-90deg]" />}
        </button>
      </div>
      <nav className="flex-1 overflow-y-auto py-2">
        {navSections.map((section) => (
          <div key={section.title}>
            <button
              type="button"
              onClick={() => toggleSection(section.title)}
              className={clsx(
                "flex w-full items-center gap-2 px-3 py-2 text-left text-xs font-medium uppercase tracking-wider text-slate-500",
                !collapsed && "justify-between"
              )}
            >
              {!collapsed && <span>{section.title}</span>}
              {!collapsed && (openSections[section.title] !== false ? <ChevronDown className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />)}
            </button>
            {(openSections[section.title] !== false || collapsed) &&
              section.items.map((item) => {
                const isActive = pathname === item.href || (item.href !== "/dashboard" && pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "flex items-center gap-2 px-3 py-2 mx-2 rounded-md text-sm transition-colors",
                      isActive ? "bg-gold/20 text-gold" : "text-slate-300 hover:bg-navy-100/30 hover:text-white",
                      collapsed && "justify-center px-2"
                    )}
                    title={collapsed ? item.label : undefined}
                  >
                    <Icon className="w-5 h-5 shrink-0" />
                    {!collapsed && <span>{item.label}</span>}
                  </Link>
                );
              })}
          </div>
        ))}
      </nav>
    </aside>
  );
}
