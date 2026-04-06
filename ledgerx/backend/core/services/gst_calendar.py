"""
Indian GST statutory due dates (hard-coded defaults for monthly filers).

- GSTR-1: 11th of the month following the tax period.
- GSTR-3B: 20th of the month following the tax period (most states; QRMP not modelled).
- GSTR-9: 31 December after the end of the financial year (FY Apr–Mar).
- Advance tax (corporate instalments): 15 Jun / 15 Sep / 15 Dec / 15 Mar of the FY.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class GstObligation:
    return_type: str
    period: str
    due_date: date
    title: str
    description: str


def month_period_key(year: int, month: int) -> str:
    return f"{month:02d}{year}"


def _next_calendar_month(year: int, month: int) -> tuple[int, int]:
    if month == 12:
        return year + 1, 1
    return year, month + 1


def gstr1_gstr3b_for_tax_period(
    year: int, month: int, gstr3b_day: int = 20
) -> tuple[GstObligation, GstObligation]:
    """Tax period = calendar month (year, month)."""
    pk = month_period_key(year, month)
    ny, nm = _next_calendar_month(year, month)
    d1 = date(ny, nm, 11)
    d3 = date(ny, nm, gstr3b_day)
    return (
        GstObligation(
            "GSTR1",
            pk,
            d1,
            f"GSTR-1 — period {month:02d}/{year}",
            "Outward supplies / B2B summary (monthly due 11th of next month).",
        ),
        GstObligation(
            "GSTR3B",
            pk,
            d3,
            f"GSTR-3B — period {month:02d}/{year}",
            "Summary return (monthly due 20th of next month for most states).",
        ),
    )


def fy_label(fy_start_year: int) -> str:
    return f"{fy_start_year}-{(fy_start_year + 1) % 100:02d}"


def gstr9_obligation(fy_start_year: int) -> GstObligation:
    """FY starts April fy_start_year (e.g. 2024 → FY 2024-25). Due 31 Dec of year fy_start+1."""
    label = fy_label(fy_start_year)
    due = date(fy_start_year + 1, 12, 31)
    return GstObligation(
        "GSTR9",
        f"FY{label}",
        due,
        f"GSTR-9 — annual (FY {label})",
        "Annual consolidated return (due 31 Dec following FY end).",
    )


def advance_obligation(fy_start_year: int, quarter: int) -> GstObligation:
    """Quarter 1–4 within Indian FY starting April fy_start_year."""
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter must be 1–4")
    label = fy_label(fy_start_year)
    period = f"ATQ{quarter}_{label}"
    if quarter == 1:
        due = date(fy_start_year, 6, 15)
    elif quarter == 2:
        due = date(fy_start_year, 9, 15)
    elif quarter == 3:
        due = date(fy_start_year, 12, 15)
    else:
        due = date(fy_start_year + 1, 3, 15)
    return GstObligation(
        "ADVANCE_TAX",
        period,
        due,
        f"Advance tax — Q{quarter} (FY {label})",
        "Corporate advance tax instalment (15 Jun / Sep / Dec / Mar).",
    )


def obligations_in_due_range(d0: date, d1: date) -> list[GstObligation]:
    """All obligations with due_date in [d0, d1] inclusive."""
    if d1 < d0:
        return []
    out: list[GstObligation] = []

    # Monthly GSTR-1 / GSTR-3B: scan tax periods (go back far enough to cover dues in window)
    y, m = d0.year - 2, 1
    end_scan = date(d1.year + 1, 12, 1)
    while date(y, m, 1) <= end_scan:
        g1, g3 = gstr1_gstr3b_for_tax_period(y, m)
        for ob in (g1, g3):
            if d0 <= ob.due_date <= d1:
                out.append(ob)
        y, m = _next_calendar_month(y, m)

    # Annual + advance tax
    for fy_start in range(d0.year - 4, d1.year + 2):
        g9 = gstr9_obligation(fy_start)
        if d0 <= g9.due_date <= d1:
            out.append(g9)
        for q in range(1, 5):
            at = advance_obligation(fy_start, q)
            if d0 <= at.due_date <= d1:
                out.append(at)

    # Dedupe (same type+period+due)
    seen: set[tuple[str, str, date]] = set()
    deduped: list[GstObligation] = []
    for ob in sorted(out, key=lambda x: (x.due_date, x.return_type, x.period)):
        key = (ob.return_type, ob.period, ob.due_date)
        if key not in seen:
            seen.add(key)
            deduped.append(ob)
    return deduped


def urgency_status(*, filed: bool, due_date: date, today: date | None = None) -> str:
    """red = overdue & not filed; amber = due within 7 days & not filed; green = filed or not urgent."""
    today = today or date.today()
    if filed:
        return "green"
    if due_date < today:
        return "red"
    if (due_date - today).days <= 7:
        return "amber"
    return "green"
