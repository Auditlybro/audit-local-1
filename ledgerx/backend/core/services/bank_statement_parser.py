"""
Bank statement parser for Indian banks.
Auto-detect format from column headers. Return standardized: {date, description, debit, credit, balance}.
Formats: SBI, HDFC, ICICI, Axis, Kotak.
"""
import csv
import io
import re
from decimal import Decimal
from typing import Any


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _parse_amount(val: Any) -> Decimal:
    if val is None or val == "":
        return Decimal("0")
    s = str(val).strip().replace(",", "")
    # Remove Dr/Cr suffix and parentheses
    s = re.sub(r"\s*[Dd]r\.?\s*$", "", s)
    s = re.sub(r"\s*[Cc]r\.?\s*$", "", s)
    s = re.sub(r"\(([^)]+)\)", r"-\1", s)
    try:
        return Decimal(s)
    except Exception:
        return Decimal("0")


def _parse_date(s: str) -> str:
    """Return ISO date string if possible."""
    s = (s or "").strip()
    if not s:
        return ""
    # DD/MM/YYYY or DD-MM-YYYY
    m = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", s)
    if m:
        d, mo, y = m.groups()
        if len(y) == 2:
            y = "20" + y
        return f"{y}-{mo.zfill(2)}-{d.zfill(2)}"
    return s


# Bank signature: set of normalized header tokens
BANK_SIGNATURES = {
    "sbi": {"date", "description", "ref", "debit", "credit", "balance"},
    "hdfc": {"date", "narration", "chq", "value date", "withdrawal", "deposit", "balance"},
    "icici": {"transaction date", "value date", "description", "amount", "balance"},
    "axis": {"tran date", "chq no", "particulars", "withdrawal", "deposit", "balance"},
    "kotak": {"transaction date", "description", "debit", "credit", "balance"},
}


def detect_bank_format(headers: list[str]) -> str:
    """Return bank key (sbi, hdfc, icici, axis, kotak) or 'generic'."""
    hnorm = set()
    for h in headers:
        hnorm.add(_normalize(h))
    best = "generic"
    best_score = 0
    for bank, sig in BANK_SIGNATURES.items():
        score = len(sig & hnorm)
        if score > best_score:
            best_score = score
            best = bank
    return best


def parse_sbi_row(row: dict[str, Any]) -> dict[str, Any]:
    """SBI: Date | Description | Ref | Debit | Credit | Balance"""
    keys = {_normalize(k): k for k in row.keys()}
    date_k = next((keys.get(n) for n in ["date", "transaction date", "value date"] if n in keys), None)
    desc_k = next((keys.get(n) for n in ["description", "particulars", "narration"] if n in keys), None)
    debit_k = next((keys.get(n) for n in ["debit", "withdrawal"] if n in keys), None)
    credit_k = next((keys.get(n) for n in ["credit", "deposit"] if n in keys), None)
    bal_k = next((keys.get(n) for n in ["balance", "running balance"] if n in keys), None)
    return {
        "date": _parse_date(row.get(date_k or "Date", "")),
        "description": str(row.get(desc_k or "Description", "")).strip(),
        "debit": _parse_amount(row.get(debit_k or "Debit")),
        "credit": _parse_amount(row.get(credit_k or "Credit")),
        "balance": _parse_amount(row.get(bal_k or "Balance")),
    }


def parse_hdfc_row(row: dict[str, Any]) -> dict[str, Any]:
    """HDFC: Date | Narration | Chq | Value Date | Withdrawal | Deposit | Balance"""
    keys = {_normalize(k): k for k in row.keys()}
    date_k = next((keys.get(n) for n in ["date", "transaction date"] if n in keys), None)
    narr_k = next((keys.get(n) for n in ["narration", "description", "particulars"] if n in keys), None)
    wdr_k = next((keys.get(n) for n in ["withdrawal", "debit"] if n in keys), None)
    dep_k = next((keys.get(n) for n in ["deposit", "credit"] if n in keys), None)
    bal_k = next((keys.get(n) for n in ["balance", "running balance"] if n in keys), None)
    return {
        "date": _parse_date(row.get(date_k or "Date", "")),
        "description": str(row.get(narr_k or "Narration", "")).strip(),
        "debit": _parse_amount(row.get(wdr_k or "Withdrawal")),
        "credit": _parse_amount(row.get(dep_k or "Deposit")),
        "balance": _parse_amount(row.get(bal_k or "Balance")),
    }


def parse_icici_row(row: dict[str, Any]) -> dict[str, Any]:
    """ICICI: Transaction Date | Value Date | Description | Amount | Balance (Amount: -ve = debit, +ve = credit)"""
    keys = {_normalize(k): k for k in row.keys()}
    date_k = next((keys.get(n) for n in ["transaction date", "date", "value date"] if n in keys), None)
    desc_k = next((keys.get(n) for n in ["description", "particulars", "narration"] if n in keys), None)
    amt_k = next((keys.get(n) for n in ["amount", "debit", "credit"] if n in keys), None)
    bal_k = next((keys.get(n) for n in ["balance", "running balance"] if n in keys), None)
    amt = _parse_amount(row.get(amt_k or "Amount"))
    return {
        "date": _parse_date(row.get(date_k or "Transaction Date", "")),
        "description": str(row.get(desc_k or "Description", "")).strip(),
        "debit": abs(amt) if amt < 0 else Decimal("0"),
        "credit": amt if amt > 0 else Decimal("0"),
        "balance": _parse_amount(row.get(bal_k or "Balance")),
    }


def parse_axis_row(row: dict[str, Any]) -> dict[str, Any]:
    """Axis: Tran Date | Chq No | Particulars | Withdrawal | Deposit | Balance"""
    keys = {_normalize(k): k for k in row.keys()}
    date_k = next((keys.get(n) for n in ["tran date", "date", "transaction date"] if n in keys), None)
    part_k = next((keys.get(n) for n in ["particulars", "description", "narration"] if n in keys), None)
    wdr_k = next((keys.get(n) for n in ["withdrawal", "debit"] if n in keys), None)
    dep_k = next((keys.get(n) for n in ["deposit", "credit"] if n in keys), None)
    bal_k = next((keys.get(n) for n in ["balance"] if n in keys), None)
    return {
        "date": _parse_date(row.get(date_k or "Tran Date", "")),
        "description": str(row.get(part_k or "Particulars", "")).strip(),
        "debit": _parse_amount(row.get(wdr_k or "Withdrawal")),
        "credit": _parse_amount(row.get(dep_k or "Deposit")),
        "balance": _parse_amount(row.get(bal_k or "Balance")),
    }


def parse_kotak_row(row: dict[str, Any]) -> dict[str, Any]:
    """Kotak: Transaction Date | Description | Debit | Credit | Balance"""
    return parse_sbi_row(row)


PARSERS = {
    "sbi": parse_sbi_row,
    "hdfc": parse_hdfc_row,
    "icici": parse_icici_row,
    "axis": parse_axis_row,
    "kotak": parse_kotak_row,
}


def parse_bank_statement(content: str | bytes) -> tuple[str, list[dict[str, Any]]]:
    """
    Parse bank statement CSV. Auto-detect bank from headers.
    Returns (bank_key, list of {date, description, debit, credit, balance}).
    """
    if isinstance(content, bytes):
        content = content.decode("utf-8", errors="replace")
    reader = csv.DictReader(io.StringIO(content))
    rows = list(reader)
    if not rows:
        return "generic", []
    headers = list(rows[0].keys())
    bank = detect_bank_format(headers)
    parser = PARSERS.get(bank, parse_sbi_row)
    out = []
    for row in rows:
        try:
            out.append(parser(row))
        except Exception:
            continue
    return bank, out
