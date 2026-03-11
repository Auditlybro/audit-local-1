"""
GST notice parser — extracts key fields from plain text notice. 100% local.
"""

from __future__ import annotations

import re
from typing import Any


def analyze_notice(notice_text: str) -> dict[str, Any]:
    """
    Extract notice_type, section_number, tax_period, amount_demanded, deadline
    from a plain text GST notice. Returns a dict suitable for JSON.
    """
    text = notice_text.strip() or ""
    out: dict[str, Any] = {
        "notice_type": "",
        "section_number": "",
        "tax_period": "",
        "amount_demanded": "",
        "deadline": "",
    }

    # Section: "Section 73", "under section 74", "u/s 61", "Sec. 75" — capture only numeric part e.g. 73, 16(4)
    section_match = re.search(
        r"(?:section|sec\.?|u/s)\s*(\d+(?:\(\d+\))?)\b",
        text,
        re.IGNORECASE,
    )
    if section_match:
        out["section_number"] = section_match.group(1).strip()

    # Notice type: infer from section or keywords
    notice_type_lower = text.lower()
    if "show cause" in notice_type_lower or "scn" in notice_type_lower:
        out["notice_type"] = "Show Cause Notice"
    elif "demand" in notice_type_lower or "order" in notice_type_lower:
        out["notice_type"] = "Demand Notice"
    elif "scrutiny" in notice_type_lower:
        out["notice_type"] = "Scrutiny Notice"
    elif "audit" in notice_type_lower:
        out["notice_type"] = "Audit Notice"
    elif "penalty" in notice_type_lower or "penal" in notice_type_lower:
        out["notice_type"] = "Penalty Notice"
    elif "interest" in notice_type_lower:
        out["notice_type"] = "Interest Notice"
    elif "block" in notice_type_lower or "itc" in notice_type_lower:
        out["notice_type"] = "ITC / Blocking Notice"
    if not out["notice_type"] and out["section_number"]:
        out["notice_type"] = f"Notice under Section {out['section_number']}"

    # Amount: prefer "TOTAL AMOUNT DEMANDED" / "total amount" label; else largest amount in notice
    def _parse_amount(s: str) -> float:
        try:
            return float(s.replace(",", "").strip())
        except (ValueError, AttributeError):
            return 0.0

    def _all_amounts(t: str) -> list[float]:
        amounts: list[float] = []
        for m in re.finditer(
            r"(?:Rs\.?|INR|₹)\s*([\d,]+(?:\.\d{2})?)|([\d,]+(?:\.\d{2})?)\s*/-|amount\s+(?:of\s+)?(?:Rs\.?|₹)?\s*([\d,]+)",
            t,
            re.IGNORECASE,
        ):
            raw = (m.group(1) or m.group(2) or m.group(3) or "").replace(",", "")
            if raw:
                val = _parse_amount(raw)
                if val > 0:
                    amounts.append(val)
        return amounts

    # Look for TOTAL AMOUNT DEMANDED or total amount (demanded) first
    total_demanded_match = re.search(
        r"total\s+amount\s+(?:demanded|payable|due)?\s*[:\s]*(?:Rs\.?|INR|₹)?\s*([\d,]+(?:\.\d{2})?)",
        text,
        re.IGNORECASE,
    )
    if total_demanded_match:
        out["amount_demanded"] = total_demanded_match.group(1).replace(",", "")
    if not out["amount_demanded"]:
        all_amts = _all_amounts(text)
        if all_amts:
            out["amount_demanded"] = str(int(max(all_amts)))
        else:
            amt_plain = re.search(r"amount\s+(?:of\s+)?(?:Rs\.?|₹)?\s*([\d,]+)", text, re.IGNORECASE)
            if amt_plain:
                out["amount_demanded"] = amt_plain.group(1).replace(",", "")

    # Tax period: "FY 2023-24", "April 2024", "GSTIN period 01/2024", "quarter ending June 2024"
    period_match = re.search(
        r"(?:FY|financial year|tax period|period)\s*[:\s]*(\d{4}[-/]\d{2,4}|\w+\s*\d{4}|\d{2}/\d{4})",
        text,
        re.IGNORECASE,
    )
    if period_match:
        out["tax_period"] = period_match.group(1).strip()
    if not out["tax_period"]:
        month_year = re.search(
            r"(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4}",
            text,
            re.IGNORECASE,
        )
        if month_year:
            out["tax_period"] = month_year.group(0).strip()

    # Deadline: "within 30 days", "by 15.06.2024", "due date 31/05/2024", "reply by 20th May 2024"
    deadline_match = re.search(
        r"(?:by|before|on|due\s+date|reply\s+by)\s*[:\s]*(\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{1,2}(?:st|nd|rd|th)?\s+(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{4})",
        text,
        re.IGNORECASE,
    )
    if deadline_match:
        out["deadline"] = deadline_match.group(1).strip()
    if not out["deadline"]:
        within = re.search(r"within\s+(\d+)\s+days", text, re.IGNORECASE)
        if within:
            out["deadline"] = f"Within {within.group(1)} days"

    return out
