"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMutation } from "@tanstack/react-query";
import { authApi } from "@/lib/api";
import { useAppStore } from "@/lib/store";
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

export default function LoginPage() {
  const router = useRouter();
  const { setUser, setCompanyId } = useAppStore();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [googleLoading, setGoogleLoading] = useState(false);
  const [msLoading, setMsLoading] = useState(false);
  const [appleLoading, setAppleLoading] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const [isNewUser, setIsNewUser] = useState(false);
  const [welcomeName, setWelcomeName] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

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
      setUser({
        id: me.id,
        email: me.email,
        name: me.name,
        role: me.role,
        org_id: me.org_id,
      });
      const { data: companies } = await (
        await import("@/lib/api")
      ).companiesApi.list();
      setWelcomeName(me.name || me.email.split("@")[0]);
      setIsNewUser(companies.length === 0);
      setLoginSuccess(true);
      setGoogleLoading(true);
      setTimeout(() => {
        if (companies.length > 0) {
          setCompanyId(companies[0].id);
          router.push("/dashboard");
        } else {
          router.push("/register?step=3");
        }
      }, 1200);
    },
  });

  const [googleError, setGoogleError] = useState("");

  const googleLogin = useMutation({
    mutationFn: (credential: string) => authApi.google({ credential }),
    onSuccess: async (res) => {
      try {
        const { access_token, refresh_token } = res.data;
        if (typeof window !== "undefined") {
          localStorage.setItem("access_token", access_token);
          localStorage.setItem("refresh_token", refresh_token);
        }
        const { data: me } = await authApi.me();
        setUser({
          id: me.id,
          email: me.email,
          name: me.name,
          role: me.role,
          org_id: me.org_id,
        });
        const { data: companies } = await (
          await import("@/lib/api")
        ).companiesApi.list();
        setWelcomeName(me.name || me.email.split("@")[0]);
        setIsNewUser(companies.length === 0);
        setLoginSuccess(true);
        setTimeout(() => {
          if (companies.length > 0) {
            setCompanyId(companies[0].id);
            router.push("/dashboard");
          } else {
            // First-time Google user → send to company setup wizard
            router.push("/register?step=3");
          }
        }, 1200);
      } catch (err) {
        console.error("Google login post-auth failed:", err);
        setGoogleError(
          "Login succeeded but failed to load your account. Please try again.",
        );
        setGoogleLoading(false);
      }
    },
    onError: (err) => {
      console.error("Google login API call failed:", err);
      setGoogleError("Google sign-in failed. Please try again.");
      setGoogleLoading(false);
    },
    onSettled: () => {
      // Don't turn off loading on success yet, let the redirect handle it
    },
  });

  const appleLogin = useMutation({
    mutationFn: (credential: string) => authApi.apple({ credential }),
    onSuccess: async (res) => {
      // Logic same as googleLogin.onSuccess
      const { access_token, refresh_token } = res.data;
      if (typeof window !== "undefined") {
        localStorage.setItem("access_token", access_token);
        localStorage.setItem("refresh_token", refresh_token);
      }
      const { data: me } = await authApi.me();
      setUser({
        id: me.id,
        email: me.email,
        name: me.name,
        role: me.role,
        org_id: me.org_id,
      });
      const { data: companies } = await (
        await import("@/lib/api")
      ).companiesApi.list();
      setWelcomeName(me.name || me.email.split("@")[0]);
      setIsNewUser(companies.length === 0);
      setLoginSuccess(true);
      setTimeout(() => {
        if (companies.length > 0) {
          setCompanyId(companies[0].id);
          router.push("/dashboard");
        } else {
          router.push("/register?step=3");
        }
      }, 1200);
    },
    onError: (err) => {
      console.error("Apple login failed:", err);
      setErrorMsg("Apple sign-in failed.");
      setAppleLoading(false);
    },
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
      setUser({
        id: me.id,
        email: me.email,
        name: me.name,
        role: me.role,
        org_id: me.org_id,
      });
      const { data: companies } = await (
        await import("@/lib/api")
      ).companiesApi.list();
      setWelcomeName(me.name || me.email.split("@")[0]);
      setIsNewUser(companies.length === 0);
      setLoginSuccess(true);
      setTimeout(() => {
        if (companies.length > 0) {
          setCompanyId(companies[0].id);
          router.push("/dashboard");
        } else {
          router.push("/register?step=3");
        }
      }, 1200);
    },
    onError: (err) => {
      console.error("Microsoft login failed:", err);
      setErrorMsg("Microsoft sign-in failed.");
      setMsLoading(false);
    },
  });

  const handleMsLogin = async () => {
    setMsLoading(true);
    try {
      const loginResponse = await msalInstance.loginPopup({
        scopes: ["user.read", "openid", "profile", "email"],
      });
      if (loginResponse.idToken) {
        msLogin.mutate(loginResponse.idToken);
      } else {
        setMsLoading(false);
      }
    } catch (err) {
      console.error(err);
      setMsLoading(false);
    }
  };

  return (
    <MsalProvider instance={msalInstance}>
      <GoogleOAuthProvider
        clientId={
          process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "YOUR_GOOGLE_CLIENT_ID"
        }
      >
        <div className="relative rounded-2xl border border-slate-200 dark:border-navy-100/20 bg-white dark:bg-navy-400/80 p-8 shadow-xl w-full max-w-md">
          {(googleLoading || msLoading || appleLoading) && (
            <div className="absolute inset-0 z-50 flex flex-col items-center justify-center rounded-2xl bg-white dark:bg-navy-400/95 backdrop-blur-sm shadow-2xl transition-all duration-300">
              {loginSuccess ? (
                <div className="flex flex-col items-center animate-in fade-in zoom-in duration-300">
                  <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-500/20 text-emerald-400 mb-4">
                    <svg
                      className="h-8 w-8"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                      strokeWidth={3}
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-1">
                    {isNewUser ? "Welcome to LedgerX!" : "Welcome back!"}
                  </h2>
                  <p className="text-sm text-slate-600 dark:text-slate-300">
                    {welcomeName}
                  </p>
                  <div className="mt-8 flex items-center gap-2 text-gold opacity-80">
                    <div className="h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                    <span className="text-xs uppercase tracking-wider">
                      {isNewUser
                        ? "Redirecting to setup"
                        : "Preparing dashboard"}
                    </span>
                  </div>
                </div>
              ) : (
                <div
                  className="flex flex-col items-center animate-in fade-in duration-300 cursor-pointer"
                  onClick={() => {
                    setGoogleLoading(false);
                    setMsLoading(false);
                    setAppleLoading(false);
                  }}
                >
                  <div className="h-12 w-12 animate-spin rounded-full border-3 border-gold border-t-transparent mb-6" />
                  <p className="text-base font-medium text-slate-200">
                    Signing you in securely…
                  </p>
                  <p className="mt-3 text-xs text-slate-500">
                    Click anywhere to cancel
                  </p>
                </div>
              )}
            </div>
          )}
          {(googleError || errorMsg) && (
            <div className="mb-4 rounded-lg bg-red-500/20 p-3 text-sm text-red-300">
              {googleError || errorMsg}
              <button
                onClick={() => {
                  setGoogleError("");
                  setErrorMsg("");
                }}
                className="ml-2 underline"
              >
                Dismiss
              </button>
            </div>
          )}
          <div className="mb-8 text-center">
            <h1 className="text-2xl font-bold text-gold">LedgerX</h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Sign in to your account
            </p>
            <p className="mt-2 text-xs text-slate-500">
              Example: demo@ledgerx.in / demo123
            </p>
          </div>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              login.mutate();
            }}
            className="space-y-4"
          >
            <div>
              <label className="block text-sm font-medium text-slate-600 dark:text-slate-300">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white placeholder-slate-500"
                placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-600 dark:text-slate-300">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-slate-200 dark:border-navy-100/30 bg-slate-50 dark:bg-navy-300 px-3 py-2 text-slate-900 dark:text-white"
              />
            </div>
            <label className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
              <input
                type="checkbox"
                checked={remember}
                onChange={(e) => setRemember(e.target.checked)}
                className="rounded"
              />
              Remember me
            </label>
            {login.isError && (
              <p className="text-sm text-red-400">
                {login.error &&
                typeof login.error === "object" &&
                "response" in login.error
                  ? (
                      login.error as {
                        response?: {
                          data?: { detail?: string };
                          status?: number;
                        };
                      }
                    ).response?.data?.detail || "Invalid email or password."
                  : (login.error as Error)?.message ||
                    "Invalid email or password."}
                {(!login.error ||
                  typeof login.error !== "object" ||
                  !("response" in login.error)) &&
                  " Check backend is running on the port in NEXT_PUBLIC_API_URL."}
              </p>
            )}
            <button
              type="submit"
              disabled={login.isPending}
              className="w-full rounded-lg bg-gold py-2.5 font-medium text-navy hover:bg-gold-light disabled:opacity-50"
            >
              {login.isPending ? "Signing in…" : "Sign in with Password"}
            </button>
          </form>

          <div className="mt-6 flex items-center justify-between">
            <span className="w-1/5 border-b border-slate-200 dark:border-navy-100/30"></span>
            <span className="text-xs text-slate-500 uppercase tracking-widest">
              Or continue with
            </span>
            <span className="w-1/5 border-b border-slate-200 dark:border-navy-100/30"></span>
          </div>

          <div className="mt-6 flex flex-col gap-3">
            {/* Custom Google Button to match MS/Apple */}
            <div className="relative group">
              <div className="absolute inset-0.5 rounded bg-black opacity-0 group-hover:opacity-5 transition-opacity pointer-events-none" />
              <GoogleLogin
                onSuccess={(credentialResponse) => {
                  if (credentialResponse.credential) {
                    setGoogleLoading(true);
                    googleLogin.mutate(credentialResponse.credential);
                  }
                }}
                onError={() => {
                  setGoogleLoading(false);
                  console.log("Login Failed");
                }}
                theme="outline"
                shape="rectangular"
                text="signin_with"
                size="large"
                width="100%"
              />
            </div>

            <button
              onClick={handleMsLogin}
              className="flex items-center w-full h-[40px] px-[12px] rounded border border-[#dadce0] bg-white text-[#3c4043] font-medium hover:bg-[#f8f9fa] transition-colors"
            >
              <div className="flex items-center justify-center w-[20px] h-[20px]">
                <svg className="w-5 h-5" viewBox="0 0 23 23">
                  <path fill="#f3f3f3" d="M0 0h23v23H0z" />
                  <path fill="#f35325" d="M1 1h10v10H1z" />
                  <path fill="#81bc06" d="M12 1h10v10H12z" />
                  <path fill="#05a6f0" d="M1 12h10v10H1z" />
                  <path fill="#ffba08" d="M12 12h10v10H12z" />
                </svg>
              </div>
              <span className="flex-1 text-center pr-5 text-sm">
                Continue with Microsoft
              </span>
            </button>

            <AppleSignin
              authOptions={{
                clientId: process.env.NEXT_PUBLIC_APPLE_CLIENT_ID || "",
                scope: "email name",
                redirectURI:
                  typeof window !== "undefined" ? window.location.origin : "",
                usePopup: true,
              }}
              uiType="dark"
              onSuccess={(response: Record<string, unknown>) => {
                if ((response.authorization as Record<string, unknown>)?.id_token) {
                  setAppleLoading(true);
                  appleLogin.mutate((response.authorization as Record<string, unknown>).id_token as string);
                }
              }}
              onError={(error: Record<string, unknown>) => {
                console.error(error);
                setErrorMsg("Apple sign-in failed.");
              }}
              render={(props: Record<string, unknown>) => (
                <button
                  {...props}
                  className="flex items-center w-full h-[40px] px-[12px] rounded border border-[#dadce0] bg-white text-[#3c4043] font-medium hover:bg-[#f8f9fa] transition-colors"
                >
                  <div className="flex items-center justify-center w-[20px] h-[20px]">
                    <svg className="w-5 h-5 fill-black" viewBox="0 0 384 512">
                      <path d="M318.7 268.7c-.2-36.7 16.4-64.4 50-84.8-18.8-26.9-47.2-41.7-84.7-44.6-35.5-2.8-74.3 20.7-88.5 20.7-15 0-49.4-19.7-76.4-19.7C63.3 141.2 4 184.8 4 273.5q0 39.3 14.4 81.2c12.8 36.7 59 126.7 107.2 125.2 25.2-.6 43-17.9 75.8-17.9 31.8 0 48.3 17.9 76.4 17.9 48.6-.7 90.4-82.5 102.6-119.3-65.2-30.7-61.7-90-61.7-91.9zm-56.6-164.2c27.3-32.4 24.8-61.9 24-72.5-24.1 1.4-52 16.4-67.9 34.9-17.5 19.8-27.8 44.3-25.6 71.9 26.1 2 49.9-11.4 69.5-34.3z" />
                    </svg>
                  </div>
                  <span className="flex-1 text-center pr-5 text-sm">
                    Continue with Apple
                  </span>
                </button>
              )}
            />
          </div>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            Don&apos;t have an account?{" "}
            <Link href="/register" className="text-gold hover:underline">
              Register
            </Link>
          </p>
        </div>
      </GoogleOAuthProvider>
    </MsalProvider>
  );
}
