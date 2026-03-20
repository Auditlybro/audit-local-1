"""
Ghost Analyst: detect mismatches, duplicates, GST issues, and risk indicators.
Input: parsed vouchers + bank transactions.
Output: { mismatches, duplicates, gst_issues, risk_score 0-100, summary }.
"""
from collections import defaultdict
from decimal import Decimal
from datetime import datetime
from typing import Any


def _parse_date(s: str) -> datetime | None:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y%m%d"):
        try:
            return datetime.strptime(str(s)[:10].replace("/", "-"), fmt)
        except Exception:
            continue
    return None


def _decimal(val: Any) -> Decimal:
    if val is None:
        return Decimal("0")
    try:
        return Decimal(str(val).replace(",", ""))
    except Exception:
        return Decimal("0")


def detect_duplicate_vouchers(vouchers: list[dict]) -> list[dict]:
    """Same date + amount + party_ledger_name => duplicate candidate."""
    key_to_indices: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for i, v in enumerate(vouchers):
        date_val = v.get("date", "") or ""
        amt = _decimal(v.get("amount"))
        party = (v.get("party_ledger_name") or v.get("party_ledger") or "").strip()
        key = (str(date_val)[:10], str(amt), party)
        key_to_indices[key].append(i)
    duplicates = []
    for key, indices in key_to_indices.items():
        if len(indices) > 1:
            for idx in indices[1:]:
                duplicates.append({"index": idx, "reason": "same date+amount+party", "voucher": vouchers[idx]})
    return duplicates


def detect_ledger_bank_mismatches(
    vouchers: list[dict],
    bank_transactions: list[dict],
    bank_ledger_name: str = "",
) -> list[dict]:
    """Amount in books (for bank ledger) != bank statement => mismatch."""
    # Sum by date: books side (dr - cr) for bank ledger
    books_by_date: dict[str, Decimal] = defaultdict(Decimal)
    for v in vouchers:
        date_val = str(v.get("date", ""))[:10]
        if not date_val:
            continue
        for e in v.get("entries", []):
            name = (e.get("ledger_name") or "").strip().upper()
            if bank_ledger_name and bank_ledger_name.upper() not in name:
                continue
            if "BANK" in name or (bank_ledger_name and name == bank_ledger_name.upper()):
                dr = _decimal(e.get("dr_amount"))
                cr = _decimal(e.get("cr_amount"))
                books_by_date[date_val] += dr - cr
    # Bank side: sum (credit - debit) per date
    bank_by_date: dict[str, Decimal] = defaultdict(Decimal)
    for t in bank_transactions:
        date_val = str(t.get("date", ""))[:10]
        if not date_val:
            continue
        bank_by_date[date_val] += _decimal(t.get("credit")) - _decimal(t.get("debit"))
    mismatches = []
    all_dates = set(books_by_date) | set(bank_by_date)
    for d in all_dates:
        diff = books_by_date.get(d, Decimal("0")) - bank_by_date.get(d, Decimal("0"))
        if abs(diff) > Decimal("0.01"):
            mismatches.append({
                "date": d,
                "books_net": str(books_by_date.get(d, 0)),
                "bank_net": str(bank_by_date.get(d, 0)),
                "difference": str(diff),
            })
    return mismatches


def detect_missing_gst(vouchers: list[dict]) -> list[dict]:
    """Taxable sale/purchase without corresponding CGST/SGST/IGST ledger entry."""
    gst_ledger_keywords = ("CGST", "SGST", "IGST", "GST", "CESS")
    issues = []
    for i, v in enumerate(vouchers):
        vtype = (v.get("voucher_type") or "").upper()
        if vtype not in ("SALES", "PURCHASE", "CREDIT_NOTE", "DEBIT_NOTE"):
            continue
        entries = v.get("entries", [])
        has_gst_entry = any(
            any(kw in (e.get("ledger_name") or "").upper() for kw in gst_ledger_keywords)
            for e in entries
        )
        total = sum(_decimal(e.get("dr_amount")) + _decimal(e.get("cr_amount")) for e in entries)
        if total > 0 and not has_gst_entry:
            issues.append({"index": i, "reason": "taxable voucher without GST ledger", "voucher": v})
    return issues


def detect_itc_without_purchase(vouchers: list[dict]) -> list[dict]:
    """ITC ledger entry without a corresponding purchase voucher (simplified: ITC entry with no purchase in same period)."""
    issues = []
    purchase_dates: set[str] = set()
    for v in vouchers:
        if (v.get("voucher_type") or "").upper() == "PURCHASE":
            purchase_dates.add(str(v.get("date", ""))[:10])
    for i, v in enumerate(vouchers):
        entries = v.get("entries", [])
        for e in entries:
            name = (e.get("ledger_name") or "").upper()
            if "ITC" not in name and "INPUT TAX" not in name:
                continue
            if "CGST" in name or "SGST" in name or "IGST" in name:
                vdate = str(v.get("date", ""))[:10]
                if vdate not in purchase_dates:
                    issues.append({"index": i, "reason": "ITC entry without purchase on same date", "voucher": v})
                break
    return issues


def detect_payments_without_bill_ref(vouchers: list[dict]) -> list[dict]:
    """Payment/Contra to party without bill reference."""
    issues = []
    for i, v in enumerate(vouchers):
        vtype = (v.get("voucher_type") or "").upper()
        if vtype not in ("PAYMENT", "CONTRA"):
            continue
        entries = v.get("entries", [])
        has_bill_ref = any(e.get("bill_ref") for e in entries)
        party = v.get("party_ledger_name") or v.get("party_ledger") or ""
        if party and not has_bill_ref:
            issues.append({"index": i, "reason": "payment without bill reference", "voucher": v})
    return issues


def detect_round_figure_anomalies(vouchers: list[dict], threshold: Decimal = Decimal("1000")) -> list[dict]:
    """Unusual round-figure transactions (e.g. exact 50000, 100000) as fraud indicator."""
    issues = []
    for i, v in enumerate(vouchers):
        amt = _decimal(v.get("amount"))
        if amt < threshold:
            continue
        if amt % Decimal("10000") == 0 or amt % Decimal("50000") == 0:
            issues.append({"index": i, "reason": "round-figure transaction", "amount": str(amt), "voucher": v})
    return issues


def detect_entries_after_fy_close(vouchers: list[dict], fy_end: str = "03-31") -> list[dict]:
    """Entries dated after financial year end (default March 31)."""
    issues = []
    for i, v in enumerate(vouchers):
        dt = _parse_date(v.get("date", ""))
        if not dt:
            continue
        month_day = (dt.month, dt.day)
        if fy_end == "03-31" and (month_day > (3, 31)):
            issues.append({"index": i, "reason": "after FY close (post March 31)", "date": str(v.get("date")), "voucher": v})
    return issues


def detect_negative_stock(
    vouchers: list[dict],
    opening_stock: dict[str, Decimal],
) -> list[dict]:
    """Sold more than available (simplified: delivery/sales reducing stock below zero)."""
    stock: dict[str, Decimal] = dict(opening_stock)
    issues = []
    for i, v in enumerate(vouchers):
        for inv in v.get("inventory_lines", []):
            item = (inv.get("stock_item") or inv.get("STOCKITEMNAME") or "").strip()
            qty = _decimal(inv.get("quantity") or inv.get("ACTUALQTY"))
            vtype = (v.get("voucher_type") or "").upper()
            if vtype in ("SALES", "DELIVERY_NOTE", "DELIVERY NOTE"):
                qty = -abs(qty)
            elif vtype in ("PURCHASE", "RECEIPT_NOTE", "RECEIPT NOTE"):
                qty = abs(qty)
            else:
                continue
            if not item:
                continue
            stock[item] = stock.get(item, Decimal("0")) + qty
            if stock[item] < Decimal("0"):
                issues.append({
                    "index": i,
                    "reason": "negative stock",
                    "item": item,
                    "balance": str(stock[item]),
                    "voucher": v,
                })
    return issues


def run_ghost_analyst(
    vouchers: list[dict],
    bank_transactions: list[dict] | None = None,
    bank_ledger_name: str = "",
    fy_end: str = "03-31",
    opening_stock: dict[str, Decimal] | None = None,
) -> dict[str, Any]:
    """
    Run all checks. Returns:
    { mismatches, duplicates, gst_issues, risk_score 0-100, summary }.
    """
    bank_transactions = bank_transactions or []
    opening_stock = opening_stock or {}

    duplicates = detect_duplicate_vouchers(vouchers)
    mismatches = detect_ledger_bank_mismatches(vouchers, bank_transactions, bank_ledger_name)
    gst_issues = detect_missing_gst(vouchers)
    itc_issues = detect_itc_without_purchase(vouchers)
    payment_ref_issues = detect_payments_without_bill_ref(vouchers)
    round_figure = detect_round_figure_anomalies(vouchers)
    after_fy = detect_entries_after_fy_close(vouchers, fy_end)
    negative_stock = detect_negative_stock(vouchers, opening_stock)

    gst_issues_combined = gst_issues + itc_issues
    categories = [
        ("duplicates", len(duplicates)),
        ("mismatches", len(mismatches)),
        ("gst_issues", len(gst_issues_combined)),
        ("payments_without_bill_ref", len(payment_ref_issues)),
        ("round_figure", len(round_figure)),
        ("after_fy_close", len(after_fy)),
        ("negative_stock", len(negative_stock)),
    ]
    total_issues = sum(c[1] for c in categories)
    # Risk score 0-100: weight duplicates and mismatches higher
    risk = min(100, (
        len(duplicates) * 5 +
        len(mismatches) * 15 +
        len(gst_issues_combined) * 10 +
        len(payment_ref_issues) * 3 +
        len(round_figure) * 2 +
        len(after_fy) * 5 +
        len(negative_stock) * 10
    ))

    summary = f"Found {total_issues} issues across {sum(1 for _, n in categories if n > 0)} categories."

    return {
        "mismatches": mismatches,
        "duplicates": duplicates,
        "gst_issues": gst_issues_combined,
        "payments_without_bill_ref": payment_ref_issues,
        "round_figure_anomalies": round_figure,
        "entries_after_fy_close": after_fy,
        "negative_stock": negative_stock,
        "risk_score": risk,
        "summary": summary,
    }
