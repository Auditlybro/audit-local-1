"""
Tax Optimiser: analyze ledger entries for the year; find ITC not claimed, exempt under-utilisation,
composition eligibility, Section 80 deductions, depreciation opportunities.
Input: company_id, financial_year (or ledger entries for that year).
Output: [ { finding, potential_saving, section_reference, action } ].
"""
from collections import defaultdict
from decimal import Decimal
from typing import Any


def _decimal(v: Any) -> Decimal:
    if v is None:
        return Decimal("0")
    try:
        return Decimal(str(v).replace(",", ""))
    except Exception:
        return Decimal("0")


def find_itc_not_claimed(entries: list[dict], purchase_ledgers: set[str]) -> list[dict]:
    """Purchase ledger entries without a matching ITC (CGST/SGST/IGST input) entry in same period."""
    # Group by date/voucher: purchases vs ITC
    by_key: dict[str, dict] = defaultdict(lambda: {"purchase": Decimal("0"), "itc": Decimal("0")})
    for e in entries:
        name = (e.get("ledger_name") or "").strip().upper()
        dr = _decimal(e.get("dr_amount"))
        cr = _decimal(e.get("cr_amount"))
        key = e.get("voucher_date") or e.get("date") or ""
        if any(p in name for p in purchase_ledgers):
            by_key[key]["purchase"] += dr - cr
        if "ITC" in name or "INPUT" in name and ("CGST" in name or "SGST" in name or "IGST" in name):
            by_key[key]["itc"] += dr - cr
    findings = []
    for k, v in by_key.items():
        if v["purchase"] > 0 and v["itc"] == 0:
            findings.append({
                "finding": "Purchase without ITC entry in same period",
                "potential_saving": str(v["purchase"]),
                "section_reference": "Section 16, CGST Act; Rule 36(4)",
                "action": "Book eligible ITC in GSTR-3B and maintain invoice details.",
            })
    return findings


def find_exempt_under_utilisation(entries: list[dict]) -> list[dict]:
    """Exempt supplies: check if common exempt categories are under-utilised (simplified)."""
    exempt_keywords = ("EXEMPT", "NIL RATED", "NON-GST")
    total_turnover = Decimal("0")
    exempt_turnover = Decimal("0")
    for e in entries:
        name = (e.get("ledger_name") or "").upper()
        amt = _decimal(e.get("dr_amount")) + _decimal(e.get("cr_amount"))
        if "SALES" in name or "REVENUE" in name:
            total_turnover += amt
        if any(k in name for k in exempt_keywords):
            exempt_turnover += amt
    findings = []
    if total_turnover > 0 and exempt_turnover / total_turnover < Decimal("0.1"):
        findings.append({
            "finding": "Low proportion of exempt supplies; consider documenting exempt/nil-rated supplies.",
            "potential_saving": "Reduced scrutiny on mixed supplies",
            "section_reference": "Section 17(2), (3) - apportionment of ITC",
            "action": "Maintain clear bifurcation of taxable vs exempt supplies for ITC reversal.",
        })
    return findings


def check_composition_eligibility(entries: list[dict], turnover_cap: Decimal = Decimal("50_00_000")) -> list[dict]:
    """If turnover below cap, composition scheme may be eligible."""
    total_turnover = Decimal("0")
    for e in entries:
        name = (e.get("ledger_name") or "").upper()
        amt = _decimal(e.get("dr_amount")) + _decimal(e.get("cr_amount"))
        if "SALES" in name or "REVENUE" in name or "TURNOVER" in name:
            total_turnover += amt
    findings = []
    if total_turnover > 0 and total_turnover <= turnover_cap:
        findings.append({
            "finding": "Turnover within composition scheme limit; assess eligibility under Section 10.",
            "potential_saving": "Lower compliance and tax under composition",
            "section_reference": "Section 10, CGST Act",
            "action": "Evaluate composition scheme eligibility and opt-in if beneficial.",
        })
    return findings


def find_section_80_deductions(entries: list[dict]) -> list[dict]:
    """Income Tax: identify expenses that may qualify for Section 80 deductions (simplified)."""
    findings = []
    keywords_80 = [("80G", "Donations"), ("80C", "LIC/PPF/ELSS"), ("80D", "Health insurance")]
    for code, desc in keywords_80:
        for e in entries:
            name = (e.get("ledger_name") or "").upper()
            if code in name or desc.upper() in name:
                findings.append({
                    "finding": f"Expense possibly eligible for Section {code} deduction.",
                    "potential_saving": "Reduce taxable income",
                    "section_reference": f"Section {code}, Income Tax Act",
                    "action": f"Ensure proof of payment and eligibility for {code} claim in ITR.",
                })
                break
    return findings


def find_depreciation_opportunities(entries: list[dict]) -> list[dict]:
    """Identify asset purchases and suggest depreciation optimisation (e.g. higher WDV in initial years)."""
    asset_keywords = ("FIXED ASSET", "MACHINERY", "EQUIPMENT", "VEHICLE", "DEPRECIATION")
    findings = []
    for e in entries:
        name = (e.get("ledger_name") or "").upper()
        if any(k in name for k in asset_keywords):
            findings.append({
                "finding": "Capital expenditure detected; review depreciation method and useful life.",
                "potential_saving": "Optimal timing under Companies Act / Income Tax rates",
                "section_reference": "Section 32, Income Tax Act; Ind AS 16",
                "action": "Align book depreciation with tax and consider partial year convention.",
            })
            break
    return findings


def run_tax_optimiser(
    company_id: str,
    financial_year: str,
    entries: list[dict],
    purchase_ledger_names: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Analyze ledger entries for the financial year.
    entries: list of { ledger_name, dr_amount, cr_amount, date/voucher_date, ... }.
    Returns: [ { finding, potential_saving, section_reference, action } ].
    """
    purchase_ledgers = set((p or "").strip().upper() for p in (purchase_ledger_names or []))
    if not purchase_ledgers:
        purchase_ledgers = {"PURCHASE", "PURCHASES", "COST OF GOODS"}

    result = []
    result.extend(find_itc_not_claimed(entries, purchase_ledgers))
    result.extend(find_exempt_under_utilisation(entries))
    result.extend(check_composition_eligibility(entries))
    result.extend(find_section_80_deductions(entries))
    result.extend(find_depreciation_opportunities(entries))
    return result
