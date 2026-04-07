import { create } from "zustand";
import { persist } from "zustand/middleware";

type User = { id: string; email: string; name: string | null; role: string; org_id: string | null };

type AppState = {
  user: User | null;
  companyId: string | null;
  companies: { id: string; name: string }[];
  setUser: (u: User | null) => void;
  setCompanyId: (id: string | null) => void;
  setCompanies: (c: { id: string; name: string }[]) => void;
};

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      user: null,
      companyId: null,
      companies: [],
      setUser: (user) => set({ user }),
      setCompanyId: (companyId) => set({ companyId }),
      setCompanies: (companies) => set({ companies }),
    }),
    { name: "ledgerx-app" }
  )
);

export const useNavStore = create<{
  isNavigating: boolean;
  setIsNavigating: (v: boolean) => void;
}>((set) => ({
  isNavigating: false,
  setIsNavigating: (isNavigating) => set({ isNavigating }),
}));
