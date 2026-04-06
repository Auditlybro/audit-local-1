/**
 * Typed API client for LedgerX backend.
 * Base URL: http://localhost:8000
 * Auto-attach JWT, 401 → redirect to login
 */

import axios, { type AxiosInstance } from "axios";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("access_token");
}

function clearAndRedirect(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  window.location.href = "/login";
}

export const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      original._retry = true;
      const refresh = localStorage.getItem("refresh_token");
      if (refresh) {
        try {
          const { data } = await axios.post(BASE_URL + "/auth/refresh", { refresh_token: refresh });
          localStorage.setItem("access_token", data.access_token);
          localStorage.setItem("refresh_token", data.refresh_token);
          original.headers.Authorization = `Bearer ${data.access_token}`;
          return api(original);
        } catch {
          clearAndRedirect();
          return Promise.reject(err);
        }
      }
      clearAndRedirect();
    }
    return Promise.reject(err);
  }
);

// --- Auth ---
export const authApi = {
  register: (body: {
    email: string;
    name?: string;
    password: string;
    org_name?: string;
  }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/register", body),
  login: (body: { email: string; password: string }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/login", body),
  refresh: (body: { refresh_token: string }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/refresh", body),
  me: () =>
    api.get<{
      id: string;
      email: string;
      name: string | null;
      role: string;
      org_id: string | null;
    }>("/auth/me"),
  otpSend: (body: { email: string }) =>
    api.post<{ message: string }>("/auth/otp/send", body),
  otpVerify: (body: { email: string; code: string }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/otp/verify", body),
  google: (body: { credential: string }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/google", body),
  apple: (body: { credential: string }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/apple", body),
  microsoft: (body: { credential: string }) =>
    api.post<{
      access_token: string;
      refresh_token: string;
      expires_in: number;
    }>("/auth/microsoft", body),
};

// --- Companies ---
export type Company = {
  id: string;
  org_id: string;
  name: string;
  gstin: string | null;
  pan: string | null;
  cin: string | null;
  address: string | null;
  state_code: string | null;
  financial_year: string | null;
  logo_url: string | null;
};
export const companiesApi = {
  list: () => api.get<Company[]>("/companies"),
  get: (id: string) => api.get<Company>(`/companies/${id}`),
  create: (body: Partial<Company>) => api.post<Company>("/companies", body),
  update: (id: string, body: Partial<Company>) => api.put<Company>(`/companies/${id}`, body),
  delete: (id: string) => api.delete(`/companies/${id}`),
};

// --- Ledgers ---
export type LedgerGroup = {
  id: string;
  company_id: string;
  name: string;
  parent_id: string | null;
  nature: string;
  is_system: boolean;
  tally_name: string | null;
};
export type Ledger = {
  id: string;
  company_id: string;
  group_id: string;
  name: string;
  alias: string | null;
  opening_balance: number;
  gstin: string | null;
  pan: string | null;
  credit_limit: number | null;
  state_code: string | null;
};
export const ledgersApi = {
  listGroups: (companyId: string) => api.get<LedgerGroup[]>(`/companies/${companyId}/ledger-groups`),
  list: (companyId: string) => api.get<Ledger[]>(`/companies/${companyId}/ledgers`),
  search: (companyId: string, q: string) => api.get<Ledger[]>(`/companies/${companyId}/ledgers/search`, { params: { q } }),
  create: (companyId: string, body: Partial<Ledger>) => api.post<Ledger>(`/companies/${companyId}/ledgers`, body),
  update: (companyId: string, ledgerId: string, body: Partial<Ledger>) =>
    api.put<Ledger>(`/companies/${companyId}/ledgers/${ledgerId}`, body),
  delete: (companyId: string, ledgerId: string) => api.delete(`/companies/${companyId}/ledgers/${ledgerId}`),
};

// --- Stock ---
export type StockItem = {
  id: string;
  company_id: string;
  group_id: string;
  name: string;
  hsn_code: string | null;
  unit: string | null;
  gst_rate: number | null;
  mrp: number | null;
  opening_qty: number;
  opening_value: number;
  reorder_level: number | null;
};
export const stockApi = {
  list: (companyId: string) => api.get<StockItem[]>(`/companies/${companyId}/stock-items`),
  create: (companyId: string, body: Partial<StockItem>) => api.post<StockItem>(`/companies/${companyId}/stock-items`, body),
  update: (companyId: string, itemId: string, body: Partial<StockItem>) =>
    api.put<StockItem>(`/companies/${companyId}/stock-items/${itemId}`, body),
  summary: (companyId: string) => api.get<{ item_id: string; name: string; quantity: number; value: number; unit: string | null }[]>(`/companies/${companyId}/stock-summary`),
};

// --- Vouchers ---
export type VoucherEntryInput = { ledger_id: string; dr_amount: number; cr_amount: number; narration?: string; bill_ref?: string; cost_centre?: string };
export type InvoiceItemInput = {
  stock_item_id: string;
  godown_id?: string;
  quantity: number;
  rate: number;
  unit?: string;
  discount_pct?: number;
  discount_amount?: number;
  taxable_value: number;
  cgst_rate?: number; cgst_amount?: number; sgst_rate?: number; sgst_amount?: number; igst_rate?: number; igst_amount?: number;
  total_amount: number;
};
export type Voucher = {
  id: string;
  company_id: string;
  voucher_type: string;
  number: string | null;
  date: string;
  party_ledger_id: string | null;
  narration: string | null;
  amount: number | null;
  reference: string | null;
  is_cancelled: boolean;
  created_at: string | null;
  entries: { id: string; ledger_id: string; dr_amount: number; cr_amount: number; narration: string | null }[];
};
export const vouchersApi = {
  list: (companyId: string, params?: { from?: string; to?: string; voucher_type?: string }) =>
    api.get<Voucher[]>(`/companies/${companyId}/vouchers`, { params }),
  get: (companyId: string, voucherId: string) => api.get<Voucher>(`/companies/${companyId}/vouchers/${voucherId}`),
  create: (companyId: string, body: {
    voucher_type: string;
    date: string;
    party_ledger_id?: string;
    narration?: string;
    reference?: string;
    cost_centre?: string;
    is_optional?: boolean;
    entries: VoucherEntryInput[];
    invoice_items?: InvoiceItemInput[];
  }) => api.post<Voucher>(`/companies/${companyId}/vouchers`, body),
  update: (companyId: string, voucherId: string, body: Partial<{ date: string; party_ledger_id: string; narration: string; reference: string; entries: VoucherEntryInput[] }>) =>
    api.put<Voucher>(`/companies/${companyId}/vouchers/${voucherId}`, body),
  cancel: (companyId: string, voucherId: string) => api.post<Voucher>(`/companies/${companyId}/vouchers/${voucherId}/cancel`),
  dayBook: (companyId: string, date: string) => api.get<{ date: string; vouchers: Voucher[] }>(`/companies/${companyId}/day-book`, { params: { date } }),
};

// --- Reports ---
export const reportsApi = {
  trialBalance: (companyId: string, from: string, to: string) =>
    api.get(`/companies/${companyId}/reports/trial-balance`, { params: { from, to } }),
  balanceSheet: (companyId: string, date: string) =>
    api.get(`/companies/${companyId}/reports/balance-sheet`, { params: { date } }),
  profitLoss: (companyId: string, from: string, to: string) =>
    api.get(`/companies/${companyId}/reports/profit-loss`, { params: { from, to } }),
  ledger: (companyId: string, ledgerId: string, from: string, to: string) =>
    api.get(`/companies/${companyId}/reports/ledger/${ledgerId}`, { params: { from, to } }),
  outstandingReceivables: (companyId: string) => api.get(`/companies/${companyId}/reports/outstanding/receivables`),
  outstandingPayables: (companyId: string) => api.get(`/companies/${companyId}/reports/outstanding/payables`),
  salesRegister: (companyId: string, from: string, to: string) =>
    api.get(`/companies/${companyId}/reports/sales-register`, { params: { from, to } }),
  stockSummary: (companyId: string) => api.get(`/companies/${companyId}/reports/stock-ageing`),
};

// --- GST ---
export const gstApi = {
  gstr1: (companyId: string, period: string) => api.get(`/companies/${companyId}/gst/gstr1`, { params: { period } }),
  gstr3b: (companyId: string, period: string) => api.get(`/companies/${companyId}/gst/gstr3b`, { params: { period } }),
  notices: (companyId: string) => api.get(`/companies/${companyId}/gst/notices`),
};

// --- Banking ---
export type BankAccount = { id: string; ledger_id: string; account_number: string; ifsc: string | null; bank_name: string | null; opening_balance: number; reconciled_till: string | null };
export const bankingApi = {
  listAccounts: (companyId: string) => api.get<BankAccount[]>(`/companies/${companyId}/banking/accounts`),
};

// --- Import ---
export const importApi = {
  history: (companyId: string) => api.get<{ sessions: { id: string; source_type: string; status: string; total_records: number; imported_records: number; created_at: string }[] }>(`/companies/${companyId}/import/history`),
};
