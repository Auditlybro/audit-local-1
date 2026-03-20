"""
Marg ERP CSV parser.
Columns: Date, VchType, VchNo, Ledger, Amount, Type(Dr/Cr), Narration, Item, Qty, Rate, Batch, Expiry
"""
import csv
import io
from decimal import Decimal
from typing import Any


# Normalize column name for fuzzy match
def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "").replace("_", "")


# Common Marg column aliases
COL_ALIASES = {
    "date": ["date", "vchdate", "voucherdate", "dt"],
    "vchtype": ["vchtype", "vouchertype", "type", "vtype"],
    "vchno": ["vchno", "vouchernumber", "vchno", "no", "number"],
    "ledger": ["ledger", "ledgername", "account"],
    "amount": ["amount", "amt", "value"],
    "type": ["type", "dr/cr", "drcr", "debitcredit"],
    "narration": ["narration", "narr", "remarks", "particulars"],
    "item": ["item", "stockitem", "product", "itemname"],
    "qty": ["qty", "quantity", "qty"],
    "rate": ["rate", "price", "unitprice"],
    "batch": ["batch", "batchno", "batch no"],
    "expiry": ["expiry", "expirydate", "expiry date", "exp date"],
}


def _match_header(header: str, row: dict[str, Any]) -> str | None:
    h = _norm(header)
    for col, aliases in COL_ALIASES.items():
        if h in aliases or any(_norm(k) in aliases for k in row.keys() if _norm(k) == h):
            for k in row.keys():
                if _norm(k) in aliases:
                    return k
    return None


def _get(row: dict[str, Any], *keys: str) -> Any:
    for k in keys:
        for key in row.keys():
            if _norm(key) in [_norm(x) for x in keys]:
                if _norm(key) == _norm(k):
                    return row.get(key)
    for k in keys:
        if k in row:
            return row[k]
    return None


def parse_marg_csv(content: str | bytes) -> list[dict[str, Any]]:
    """
    Parse Marg CSV. Standard columns: Date, VchType, VchNo, Ledger, Amount, Type(Dr/Cr), Narration, Item, Qty, Rate, Batch, Expiry.
    Returns list of normalized voucher-like dicts (one row per ledger line; group by VchNo+Date for same voucher).
    """
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return []

    # Build key map from first row
    first = rows[0]
    key_date = next((k for k in first if _norm(k) in ["date", "vchdate", "voucherdate"]), "Date")
    key_vchtype = next((k for k in first if _norm(k) in ["vchtype", "vouchertype", "type"]), "VchType")
    key_vchno = next((k for k in first if _norm(k) in ["vchno", "vouchernumber", "no"]), "VchNo")
    key_ledger = next((k for k in first if _norm(k) in ["ledger", "ledgername"]), "Ledger")
    key_amount = next((k for k in first if _norm(k) in ["amount", "amt"]), "Amount")
    key_drcr = next((k for k in first if _norm(k) in ["type", "drcr", "dr/cr", "debitcredit"]), "Type")
    key_narr = next((k for k in first if _norm(k) in ["narration", "narr", "remarks"]), "Narration")
    key_item = next((k for k in first if _norm(k) in ["item", "stockitem", "product"]), "Item")
    key_qty = next((k for k in first if _norm(k) in ["qty", "quantity"]), "Qty")
    key_rate = next((k for k in first if _norm(k) in ["rate", "price"]), "Rate")
    key_batch = next((k for k in first if _norm(k) in ["batch", "batchno"]), "Batch")
    key_expiry = next((k for k in first if _norm(k) in ["expiry", "expirydate"]), "Expiry")

    # Group by voucher (VchNo + Date)
    vouchers: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        date_val = str(r.get(key_date, "")).strip()
        vchno = str(r.get(key_vchno, "")).strip()
        vchtype = str(r.get(key_vchtype, "Journal")).strip()
        ledger = str(r.get(key_ledger, "")).strip()
        amt = r.get(key_amount)
        try:
            amount = Decimal(str(amt).replace(",", "")) if amt else Decimal("0")
        except Exception:
            amount = Decimal("0")
        drcr = str(r.get(key_drcr, "Dr")).strip().upper()
        if "CR" in drcr or drcr == "C":
            dr_amount, cr_amount = Decimal("0"), amount
        else:
            dr_amount, cr_amount = amount, Decimal("0")
        narration = str(r.get(key_narr, "")).strip()
        item = str(r.get(key_item, "")).strip()
        qty = r.get(key_qty)
        rate = r.get(key_rate)
        try:
            qty_d = Decimal(str(qty).replace(",", "")) if qty else Decimal("0")
        except Exception:
            qty_d = Decimal("0")
        try:
            rate_d = Decimal(str(rate).replace(",", "")) if rate else Decimal("0")
        except Exception:
            rate_d = Decimal("0")

        key = (date_val, vchno or str(len(vouchers)))
        if key not in vouchers:
            vouchers[key] = {
                "date": date_val,
                "voucher_type": vchtype,
                "voucher_number": vchno,
                "narration": narration,
                "entries": [],
                "inventory_lines": [],
            }
        if ledger:
            vouchers[key]["entries"].append({
                "ledger_name": ledger,
                "dr_amount": dr_amount,
                "cr_amount": cr_amount,
                "narration": narration,
            })
        if item and (qty_d or rate_d):
            vouchers[key]["inventory_lines"].append({
                "stock_item": item,
                "quantity": qty_d,
                "rate": rate_d,
                "batch": str(r.get(key_batch, "")).strip(),
                "expiry": str(r.get(key_expiry, "")).strip(),
            })

    return list(vouchers.values())
