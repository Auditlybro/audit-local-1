"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

export function ThemeToggle({ collapsed }: { collapsed?: boolean }) {
  const { theme, setTheme } = useTheme()

  return (
    <button
      onClick={() => setTheme(theme === "light" ? "dark" : "light")}
      className="flex items-center gap-2 p-2 rounded-md hover:bg-slate-200 dark:hover:bg-navy-100/30 text-slate-500 dark:text-slate-400 w-full transition-colors"
      title="Toggle theme"
    >
      <div className="relative w-5 h-5 shrink-0 flex items-center justify-center">
        <Sun className="h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0 absolute" />
        <Moon className="h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100 absolute" />
      </div>
      {!collapsed && <span className="text-sm">Theme</span>}
    </button>
  )
}
