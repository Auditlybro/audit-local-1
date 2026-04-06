"use client";

import { useState, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { authApi, companiesApi } from "@/lib/api";
import { useAppStore } from "@/lib/store";
import { GSTINInput } from "@/components/ui/GSTINInput";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider } from "@azure/msal-react";
import AppleSignin from "react-apple-signin-auth";

const msalConfig = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_MS_CLIENT_ID || "",
    authority: "https://login.microsoftonline.com/common",
    redirectUri: typeof window !== "undefined" ? window.location.origin : "",
  },
};

const msalInstance = new PublicClientApplication(msalConfig);

const STEPS = [
  "Email Setup",
  "Verify Email",
  "Company details",
  "Financial year",
  "Import data?",
  "Done",
];

function RegisterPageContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser, setCompanyId, setCompanies } = useAppStore();
  const initialStep = Number(searchParams.get("step")) || 1;
  const [step, setStep] = useState(initialStep);
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [gstin, setGstin] = useState("");
  const [pan, setPan] = useState("");
  const [stateCode, setStateCode] = useState("");
  const [fyStart, setFyStart] = useState(4); // April
  const [importChoice, setImportChoice] = useState<"tally" | "marg" | "skip">("skip");


  const sendOtp = useMutation({
    mutationFn: () => authApi.otpSend({ email }),
    onSuccess: () => setStep(2),
  });

  const verifyOtp = useMutation({
    mutationFn: () => authApi.otpVerify({ email, code: otp }),
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
      }
      const { data: me } = await authApi.me();
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role, org_id: me.org_id });
      setStep(3);
    },
  });

  const googleLogin = useMutation({
    mutationFn: (credential: string) => authApi.google({ credential }),
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
      }
      const { data: me } = await authApi.me();
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role, org_id: me.org_id });
      setStep(3); // Skip OTP, go straight to company
    }
  });

  const appleLogin = useMutation({
    mutationFn: (credential: string) => authApi.apple({ credential }),
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
      }
      const { data: me } = await authApi.me();
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role, org_id: me.org_id });
      setStep(3);
    }
  });

  const msLogin = useMutation({
    mutationFn: (credential: string) => authApi.microsoft({ credential }),
    onSuccess: async (res) => {
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
      }
      const { data: me } = await authApi.me();
      setUser({ id: me.id, email: me.email, name: me.name, role: me.role, org_id: me.org_id });
      setStep(3);
    }
  });

  const handleMsLogin = async () => {
    try {
      const loginResponse = await msalInstance.loginPopup({
        scopes: ["user.read", "openid", "profile", "email"],
      });
      if (loginResponse.idToken) {
        msLogin.mutate(loginResponse.idToken);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const finishSetup = useMutation({
    mutationFn: async () => {
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

  return (
    <MsalProvider instance={msalInstance}>
    <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID"}>
      <div className="rounded-2xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-8 shadow-xl max-w-2xl w-full">
        <div className="mb-6 text-center">
          <h1 className="text-2xl font-bold text-gold">LedgerX</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">Company setup wizard</p>
          <div className="mt-4 flex justify-center gap-1">
            {STEPS.map((_, i) => (
              <div
                key={i}
                className={`h-1.5 w-8 rounded-full ${i + 1 <= step ? "bg-gold" : "bg-slate-100 dark:bg-navy-100/30"}`}
                aria-hidden
              />
            ))}
          </div>
        </div>

        {step === 1 && (
          <div className="space-y-4">
            <h2 className="font-semibold text-slate-900 dark:text-white">Step 1: Account Email</h2>
            <input
              type="email"
              placeholder="Organization Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-500"
            />
            {sendOtp.isError && <p className="text-red-400 text-sm">Failed to send OTP. Is the backend working?</p>}

            <div className="mt-6 pt-4 border-t border-slate-200 dark:border-navy-100/30 flex flex-col items-center gap-3">
              <span className="text-xs text-slate-500 uppercase tracking-widest mb-1">Or register with</span>
              <GoogleLogin
                onSuccess={(res) => { if (res.credential) googleLogin.mutate(res.credential) }}
                onError={() => console.log("Google Failed")}
                theme="outline"
                shape="rectangular"
                width="280px"
              />

              <button 
                onClick={handleMsLogin}
                className="flex items-center w-[280px] h-[40px] px-[12px] rounded border border-[#dadce0] bg-white text-[#3c4043] font-medium hover:bg-[#f8f9fa] transition-colors"
              >
                <div className="flex items-center justify-center w-[20px] h-[20px]">
                  <svg className="w-5 h-5" viewBox="0 0 23 23">
                    <path fill="#f3f3f3" d="M0 0h23v23H0z"/><path fill="#f35325" d="M1 1h10v10H1z"/><path fill="#81bc06" d="M12 1h10v10H12z"/><path fill="#05a6f0" d="M1 12h10v10H1z"/><path fill="#ffba08" d="M12 12h10v10H12z"/>
                  </svg>
                </div>
                <span className="flex-1 text-center pr-5 text-sm">Register with Microsoft</span>
              </button>

              <AppleSignin
                authOptions={{
                  clientId: process.env.NEXT_PUBLIC_APPLE_CLIENT_ID || "",
                  scope: "email name",
                  redirectURI: typeof window !== "undefined" ? window.location.origin : "",
                  usePopup: true,
                }}
                uiType="dark"
                onSuccess={(response: Record<string, unknown>) => {
                  if ((response.authorization as Record<string, unknown>)?.id_token) {
                    appleLogin.mutate((response.authorization as Record<string, unknown>).id_token as string);
                  }
                }}
                onError={(error: Record<string, unknown>) => console.error(error)}
                render={(props: Record<string, unknown>) => (
                  <button 
                    {...props}
                    className="flex items-center w-[280px] h-[40px] px-[12px] rounded border border-[#dadce0] bg-white text-[#3c4043] font-medium hover:bg-[#f8f9fa] transition-colors"
                  >
                    <div className="flex items-center justify-center w-[20px] h-[20px]">
                      <svg className="w-5 h-5 fill-black" viewBox="0 0 384 512">
                         <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z"/>
                      </svg>
                    </div>
                    <span className="flex-1 text-center pr-5 text-sm">Register with Apple</span>
                  </button>
                )}
              />
            </div>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-4">
            <h2 className="font-semibold text-slate-900 dark:text-white">Step 2: Verify your Email</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">We sent a 6-digit code to {email}</p>
            <input
              type="text"
              placeholder="000000"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
              className="w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-3 text-slate-900 dark:text-white placeholder-slate-500 text-center tracking-[1em] text-2xl"
              maxLength={6}
            />
            {verifyOtp.isError && <p className="text-red-400 text-sm text-center">Invalid or expired code.</p>}
          </div>
        )}

        {step === 3 && (
          <div className="space-y-4">
            <h2 className="font-semibold text-slate-900 dark:text-white">Step 3: Company details</h2>
            <input
              type="text"
              placeholder="Company name"
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              className="w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-500"
            />
            <div>
              <label className="block text-sm text-slate-500 dark:text-slate-400 mb-1">GSTIN (optional)</label>
              <GSTINInput value={gstin} onChange={(v) => { setGstin(v); }} className="w-full" />
            </div>
            <input
              type="text"
              placeholder="PAN (optional)"
              value={pan}
              onChange={(e) => setPan(e.target.value.toUpperCase().slice(0, 10))}
              className="w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-500"
            />
            <input
              type="text"
              placeholder="State code (e.g. 27)"
              value={stateCode}
              onChange={(e) => setStateCode(e.target.value.replace(/\D/g, "").slice(0, 2))}
              className="w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-500"
            />
          </div>
        )}

        {step === 4 && (
          <div className="space-y-4">
            <h2 className="font-semibold text-slate-900 dark:text-white">Step 4: Financial year start</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Indian financial year is April to March.</p>
            <select
              value={fyStart}
              onChange={(e) => setFyStart(Number(e.target.value))}
              className="w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white"
            >
              <option value={1}>January</option>
              <option value={4}>April (recommended)</option>
              <option value={7}>July</option>
            </select>
          </div>
        )}

        {step === 5 && (
          <div className="space-y-4">
            <h2 className="font-semibold text-slate-900 dark:text-white">Step 5: Import existing data?</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">You can import later from the Import page.</p>
            <div className="flex gap-2">
              {(["tally", "marg", "skip"] as const).map((opt) => (
                <button
                  key={opt}
                  type="button"
                  onClick={() => setImportChoice(opt)}
                  className={`rounded-lg border px-4 py-2 text-sm capitalize ${
                    importChoice === opt ? "border-gold bg-gold/20 text-gold" : "border-slate-200 dark:border-navy-100/30 text-slate-600 dark:text-slate-300"
                  }`}
                >
                  {opt === "skip" ? "Skip" : opt === "tally" ? "Tally XML" : "Marg/Busy"}
                </button>
              ))}
            </div>
          </div>
        )}

        {step === 6 && (
          <div className="space-y-4 text-center">
            <h2 className="font-semibold text-slate-900 dark:text-white">All set!</h2>
            <p className="text-sm text-slate-500 dark:text-slate-400">Click Finish to secure your account and go to the dashboard.</p>
            {finishSetup.isError && <p className="text-red-400 text-sm">Failed to create initial company profile.</p>}
          </div>
        )}

        <div className="mt-8 flex justify-between">
          <button
            type="button"
            onClick={() => setStep((s) => Math.max(1, s - 1))}
            disabled={step === 1 || step === 3}
            className="rounded-lg border border-slate-200 dark:border-navy-100/30 px-4 py-2 text-sm text-slate-600 dark:text-slate-300 disabled:opacity-50"
          >
            Back
          </button>
          
          {step < 6 ? (
            <button
              type="button"
              onClick={() => {
                if (step === 1) sendOtp.mutate();
                else if (step === 2) verifyOtp.mutate();
                else setStep(s => s + 1);
              }}
              disabled={
                (step === 1 && (!email || sendOtp.isPending)) ||
                (step === 2 && (otp.length !== 6 || verifyOtp.isPending)) ||
                (step === 3 && !companyName)
              }
              className="rounded-lg bg-gold px-6 py-2 text-sm font-medium text-navy disabled:opacity-50"
            >
              {sendOtp.isPending || verifyOtp.isPending || googleLogin.isPending ? "Processing…" : "Next"}
            </button>
          ) : (
            <button
              type="button"
              onClick={() => finishSetup.mutate()}
              disabled={finishSetup.isPending}
              className="rounded-lg bg-gold px-6 py-2 text-sm font-medium text-navy disabled:opacity-50"
            >
              {finishSetup.isPending ? "Creating…" : "Finish Registration"}
            </button>
          )}
        </div>

        <p className="mt-8 text-center text-sm text-slate-500 dark:text-slate-400 border-t border-slate-200 dark:border-navy-100/20 pt-6">
          Already have an account? <Link href="/login" className="text-gold hover:underline">Sign in</Link>
        </p>
      </div>
    </GoogleOAuthProvider>
    </MsalProvider>
  );
}

export default function RegisterPage() {
  return (
    <Suspense fallback={<div className="flex h-screen items-center justify-center text-slate-500">Loading setup...</div>}>
      <RegisterPageContent />
    </Suspense>
  );
}
