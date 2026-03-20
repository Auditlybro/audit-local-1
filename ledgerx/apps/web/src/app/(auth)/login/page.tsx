"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/lib/api";
import { useAppStore } from "@/lib/store";

export default function LoginPage() {
  const router = useRouter();
  const { setUser, setCompanyId, setCompanies } = useAppStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);

  const login = useMutation({
    mutationFn: () => authApi.login({ email, password }),
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
        if (!remember) localStorage.removeItem("refresh_token");
      }
      const { data: me } = await authApi.me();
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role, org_id: me.org_id });
      const { data: companies } = await (await import("@/lib/api")).companiesApi.list();
      setCompanies(companies.map((c) => ({ id: c.id, name: c.name })));
      if (companies.length > 0) setCompanyId(companies[0].id);
      router.push("/dashboard");
    },
  });

  return (
    <div className="rounded-2xl border border-navy-100/20 bg-navy-400/80 p-8 shadow-xl">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-bold text-gold">LedgerX</h1>
        <p className="mt-1 text-sm text-slate-400">Sign in to your account</p>
        <p className="mt-2 text-xs text-slate-500">Demo: demo@ledgerx.in / demo123</p>
      </div>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          login.mutate();
        }}
        className="space-y-4"
      >
        <div>
          <label className="block text-sm font-medium text-slate-300">Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
            placeholder="you@example.com"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-300">Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1 w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white"
          />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-400">
          <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} className="rounded" />
          Remember me
        </label>
        {login.isError && (
          <p className="text-sm text-red-400">
            {login.error && typeof login.error === "object" && "response" in login.error
              ? (login.error as { response?: { data?: { detail?: string }; status?: number } }).response?.data?.detail || "Invalid email or password."
              : (login.error as Error)?.message || "Invalid email or password."}
            {(!login.error || typeof login.error !== "object" || !("response" in login.error)) && " Check backend is running on the port in NEXT_PUBLIC_API_URL."}
          </p>
        )}
        <button
          type="submit"
          disabled={login.isPending}
          className="w-full rounded-lg bg-gold py-2.5 font-medium text-navy hover:bg-gold-light disabled:opacity-50"
        >
          {login.isPending ? "Signing in…" : "Sign in"}
        </button>
      </form>
      <p className="mt-6 text-center text-sm text-slate-400">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="text-gold hover:underline">Register</Link>
      </p>
    </div>
  );
}
