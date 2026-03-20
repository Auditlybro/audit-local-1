/**
 * Indian number format: 1,00,000 (lakhs) and ₹
 */
export function formatINR(amount: number | string | null | undefined): string {
  if (amount == null || amount === "") return "₹0.00";
  const n = typeof amount === "string" ? parseFloat(amount) : amount;
  if (Number.isNaN(n)) return "₹0.00";
  const [intPart, decPart] = n.toFixed(2).split(".");
  const indian = intPart.length > 3
    ? intPart.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + intPart.slice(-3)
    : intPart;
  return `₹${indian}.${decPart}`;
}

export function formatINRNoSymbol(amount: number | string | null | undefined): string {
  if (amount == null || amount === "") return "0.00";
  const n = typeof amount === "string" ? parseFloat(amount) : amount;
  if (Number.isNaN(n)) return "0.00";
  const [intPart, decPart] = n.toFixed(2).split(".");
  const indian = intPart.length > 3
    ? intPart.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ",") + "," + intPart.slice(-3)
    : intPart;
  return `${indian}.${decPart}`;
}

/** DD-MMM-YYYY e.g. 01-Apr-2025 */
export function formatDateDisplay(d: Date | string | null | undefined): string {
  if (!d) return "";
  const date = typeof d === "string" ? new Date(d) : d;
  const day = date.getDate().toString().padStart(2, "0");
  const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
  const month = months[date.getMonth()];
  const year = date.getFullYear();
  return `${day}-${month}-${year}`;
}

/** Parse DD-MMM-YYYY or ISO to Date */
export function parseDateInput(s: string): Date | null {
  if (!s) return null;
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? null : d;
}
