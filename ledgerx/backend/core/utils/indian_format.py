"""Indian number and date formatting."""
from decimal import Decimal
from typing import Union


def format_inr(amount: Union[int, float, Decimal], symbol: bool = True) -> str:
    """
    Format amount in Indian style: 1,00,000 (lakhs) and append ₹.
    amount is in rupees (not paise).
    """
    if amount is None:
        return "₹0" if symbol else "0"
    x = Decimal(str(amount)).quantize(Decimal("0.01"))
    s = f"{x:,.2f}"
    # Indian: last 3 digits (after decimal) then groups of 2
    if "." in s:
        int_part, dec_part = s.rsplit(".", 1)
    else:
        int_part, dec_part = s, "00"
    if "," in int_part:
        parts = int_part.replace(",", "").strip()
        # from right: 3 (or remaining), then 2, 2, 2...
        n = len(parts)
        if n <= 3:
            int_part = parts
        else:
            right = parts[-3:]
            rest = parts[:-3]
            groups = [right]
            while rest:
                groups.append(rest[-2:])
                rest = rest[:-2]
            int_part = ",".join(reversed(groups))
    result = f"{int_part}.{dec_part}"
    if symbol:
        result = f"₹{result}"
    return result


def format_inr_paise(paise: int, symbol: bool = True) -> str:
    """Format amount given in paise (integer) to Indian INR string."""
    return format_inr(paise / 100, symbol=symbol)


def parse_inr_to_paise(value: Union[str, int, float, Decimal]) -> int:
    """Parse INR string or number to paise (integer)."""
    if value is None:
        return 0
    if isinstance(value, int):
        return value
    if isinstance(value, (float, Decimal)):
        return int(round(float(value) * 100))
    s = str(value).replace(",", "").replace("₹", "").strip()
    if not s:
        return 0
    return int(round(Decimal(s) * 100))


def format_date_display(dt) -> str:
    """Format date as DD-MMM-YYYY (e.g. 01-Apr-2025)."""
    if dt is None:
        return ""
    d = dt if hasattr(dt, "strftime") else dt
    return d.strftime("%d-%b-%Y")


MONTHS = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


def financial_year(date) -> str:
    """Return financial year string (e.g. 2024-25) for given date. FY: April–March."""
    if hasattr(date, "year") and hasattr(date, "month"):
        y, m = date.year, date.month
    else:
        return ""
    if m >= 4:
        return f"{y}-{str(y + 1)[-2:]}"
    return f"{y - 1}-{str(y)[-2:]}"
