"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { authApi, companiesApi } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { GSTINInput } from "@/components/ui/GSTINInput";

const STEPS = [
  "Personal info",
  "Company details",
  "Financial year",
  "Import data?",
  "Done",
];

export default function RegisterPage() {
  const router = useRouter();
  const { setUser, setCompanyId, setCompanies } = useAppStore();
  const [step, setStep] = useState(1);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [gstin, setGstin] = useState("");
  const [pan, setPan] = useState("");
  const [stateCode, setStateCode] = useState("");
  const [fyStart, setFyStart] = useState(4); // April
  const [importChoice, setImportChoice] = useState<"tally" | "marg" | "skip">("skip");
  const [gstinValid, setGstinValid] = useState(true);

  const register = useMutation({
    mutationFn: () =>
      authApi.register({
        email,
        name: name || undefined,
        password,
        org_name: orgName || companyName || "My Company",
      }),
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
      }
      const { data: me } = await authApi.me();
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role, org_id: me.org_id });
      await companiesApi.create({
        name: companyName || "Default Company",
        gstin: gstin || undefined,
        pan: pan || undefined,
        state_code: stateCode || undefined,
        financial_year: fyStart === 4 ? `${new Date().getFullYear()}-${String(new Date().getFullYear() + 1).slice(-2)}` : undefined,
      });
      const { data: companies } = await companiesApi.list();
      setCompanies(companies.map((c) => ({ id: c.id, name: c.name })));
      if (companies.length > 0) setCompanyId(companies[0].id);
      router.push("/dashboard");
    },
  });

  const canNext =
    (step === 1 && name && email && password) ||
    (step === 2 && companyName) ||
    (step === 3) ||
    (step === 4) ||
    (step === 5);

  return (
    <div className="rounded-2xl border border-navy-100/20 bg-navy-400/80 p-8 shadow-xl">
      <div className="mb-6 text-center">
        <h1 className="text-2xl font-bold text-gold">LedgerX</h1>
        <p className="mt-1 text-sm text-slate-400">Company setup wizard</p>
        <div className="mt-4 flex justify-center gap-1">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className={`h-1.5 w-8 rounded-full ${i + 1 <= step ? "bg-gold" : "bg-navy-100/30"}`}
              aria-hidden
            />
          ))}
        </div>
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-white">Step 1: Personal info</h2>
          <input
            type="text"
            placeholder="Full name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-white">Step 2: Company details</h2>
          <input
            type="text"
            placeholder="Company name"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
          <input
            type="text"
            placeholder="Organization name (optional)"
            value={orgName}
            onChange={(e) => setOrgName(e.target.value)}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
          <div>
            <label className="block text-sm text-slate-400">GSTIN (optional)</label>
            <GSTINInput value={gstin} onChange={(v, valid) => { setGstin(v); setGstinValid(valid); }} className="mt-1 w-full" />
          </div>
          <input
            type="text"
            placeholder="PAN (optional)"
            value={pan}
            onChange={(e) => setPan(e.target.value.toUpperCase().slice(0, 10))}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
          <input
            type="text"
            placeholder="State code (e.g. 27)"
            value={stateCode}
            onChange={(e) => setStateCode(e.target.value.replace(/\D/g, "").slice(0, 2))}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white placeholder-slate-500"
          />
        </div>
      )}

      {step === 3 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-white">Step 3: Financial year start</h2>
          <p className="text-sm text-slate-400">Indian financial year is April to March.</p>
          <select
            value={fyStart}
            onChange={(e) => setFyStart(Number(e.target.value))}
            className="w-full rounded-lg border border-navy-100/30 bg-navy-300 px-3 py-2 text-white"
          >
            <option value={1}>January</option>
            <option value={4}>April (recommended)</option>
            <option value={7}>July</option>
          </select>
        </div>
      )}

      {step === 4 && (
        <div className="space-y-4">
          <h2 className="font-semibold text-white">Step 4: Import existing data?</h2>
          <p className="text-sm text-slate-400">You can import later from the Import page.</p>
          <div className="flex gap-2">
            {(["tally", "marg", "skip"] as const).map((opt) => (
              <button
                key={opt}
                type="button"
                onClick={() => setImportChoice(opt)}
                className={`rounded-lg border px-4 py-2 text-sm capitalize ${
                  importChoice === opt ? "border-gold bg-gold/20 text-gold" : "border-navy-100/30 text-slate-300"
                }`}
              >
                {opt === "skip" ? "Skip" : opt === "tally" ? "Tally XML" : "Marg/Busy"}
              </button>
            ))}
          </div>
        </div>
      )}

      {step === 5 && (
        <div className="space-y-4 text-center">
          <h2 className="font-semibold text-white">All set!</h2>
          <p className="text-sm text-slate-400">Click Finish to create your account and go to the dashboard.</p>
          {!email && (
            <p className="text-sm text-amber-400">Go back to Step 1 and enter your email.</p>
          )}
          {!password && (
            <p className="text-sm text-amber-400">Go back to Step 1 and enter a password.</p>
          )}
          {register.isError && (
            <div className="rounded-lg border border-red-500/50 bg-red-500/10 p-3 text-left">
              <p className="text-sm font-medium text-red-400">Registration failed</p>
              <p className="mt-1 text-sm text-red-300">
                {register.error && typeof register.error === "object" && "response" in register.error
                  ? (register.error as { response?: { data?: { detail?: string }; status?: number } }).response?.data?.detail ||
                    (register.error as Error)?.message ||
                    "Invalid request."
                  : (register.error as Error)?.message || "Invalid request."}
              </p>
              <p className="mt-2 text-xs text-slate-400">
                Ensure the backend is running (e.g. npm run dev:all) and NEXT_PUBLIC_API_URL in .env is http://localhost:8001
              </p>
            </div>
          )}
          {importChoice !== "skip" && (
            <p className="text-sm text-gold">After signup you can import from the Import page.</p>
          )}
        </div>
      )}

      <div className="mt-8 flex justify-between">
        <button
          type="button"
          onClick={() => setStep((s) => Math.max(1, s - 1))}
          disabled={step === 1}
          className="rounded-lg border border-navy-100/30 px-4 py-2 text-sm text-slate-300 disabled:opacity-50"
        >
          Back
        </button>
        {step < 5 ? (
          <button
            type="button"
            onClick={() => setStep((s) => s + 1)}
            disabled={!canNext || (step === 2 && !gstinValid)}
            className="rounded-lg bg-gold px-4 py-2 text-sm font-medium text-navy disabled:opacity-50"
          >
            Next
          </button>
        ) : (
          <button
            type="button"
            onClick={() => {
              if (!email || !password) return;
              register.mutate();
            }}
            disabled={register.isPending || !email || !password}
            className="rounded-lg bg-gold px-4 py-2 text-sm font-medium text-navy disabled:opacity-50"
          >
            {register.isPending ? "Creating…" : "Finish"}
          </button>
        )}
      </div>

      <p className="mt-6 text-center text-sm text-slate-400">
        Already have an account? <Link href="/login" className="text-gold hover:underline">Sign in</Link>
      </p>
    </div>
  );
}
