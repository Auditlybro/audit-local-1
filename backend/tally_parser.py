"""
Tally XML parser — 100% local. No cloud. Parses <VOUCHER> entries from Tally ERP export.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from lxml import etree


def _text(el: etree._Element | None) -> str:
    if el is None:
        return ""
    raw = (el.text or "").strip()
    if not raw:
        raw = "".join(el.itertext()).strip()
    return raw


def _normalize_party(name: str) -> str:
    return " ".join(name.split()).lower() if name else ""


def parse_tally_xml(path: str | Path) -> list[dict[str, Any]]:
    """
    Parse a Tally XML file and return a list of normalized voucher rows.
    Each row: date, voucher_type, party_name, amount, ledger_name, narration, is_duplicate.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    tree = etree.parse(str(path))
    root = tree.getroot()

    # Tally exports may wrap content in TALLYMESSAGE or have VOUCHER at various levels
    vouchers = root.findall(".//VOUCHER")
    if not vouchers:
        vouchers = root.findall("VOUCHER")

    rows: list[dict[str, Any]] = []
    for v in vouchers:
        date_el = v.find("DATE")
        date_str = _text(date_el).replace(".", "-") if date_el is not None else ""

        voucher_type_el = v.find("VOUCHERTYPENAME") if v.find("VOUCHERTYPENAME") is not None else v.find("VOUCHERTYPE")
        voucher_type = _text(voucher_type_el)

        # Party: often PARTYLEDGERNAME or first ledger in entries
        party_el = v.find("PARTYLEDGERNAME") if v.find("PARTYLEDGERNAME") is not None else v.find("PARTYNAME")
        party_raw = _text(party_el)
        if not party_raw:
            # Fallback: first ledger entry name
            entries = v.find("ALLLEDGERENTRIES.LIST") or v.find("LEDGERENTRIES.LIST")
            if entries is not None:
                first_ledger = entries.find("LEDGERNAME") or entries.find("NAME")
                party_raw = _text(first_ledger)
        party_name = _normalize_party(party_raw)

        # Ledger entries: one row per entry when present, else one row per voucher
        parent_list = v.find("ALLLEDGERENTRIES.LIST") if v.find("ALLLEDGERENTRIES.LIST") is not None else v.find("LEDGERENTRIES.LIST")
        if parent_list is not None:
            entries = parent_list.findall("ALLLEDGERENTRIES.LIST") or parent_list.findall("LEDGERENTRIES.LIST")
            if not entries:
                entries = [parent_list]
            for entry in entries:
                ledger_el = entry.find("LEDGERNAME") if entry.find("LEDGERNAME") is not None else (entry.find("LEDGER") if entry.find("LEDGER") is not None else entry.find("NAME"))
                amount_el = entry.find("AMOUNT")
                narration_el = entry.find("NARRATION") if entry.find("NARRATION") is not None else entry.find("REMARKS")
                amount_str = _text(amount_el)
                try:
                    amount = float(amount_str) if amount_str else 0.0
                except ValueError:
                    amount = 0.0
                ledger_name = _text(ledger_el) or party_raw
                narration = _text(narration_el)
                rows.append({
                    "date": date_str,
                    "voucher_type": voucher_type.strip(),
                    "party_name": party_name or _normalize_party(ledger_name),
                    "amount": amount,
                    "ledger_name": ledger_name.strip(),
                    "narration": narration,
                    "is_duplicate": False,
                })
        else:
            amount_el = v.find("AMOUNT")
            amount_str = _text(amount_el)
            try:
                amount = float(amount_str) if amount_str else 0.0
            except ValueError:
                amount = 0.0
            ledger_el = v.find("LEDGERNAME") if v.find("LEDGERNAME") is not None else v.find("LEDGER")
            ledger_name = _text(ledger_el) or party_raw
            narration_el = v.find("NARRATION") if v.find("NARRATION") is not None else v.find("REMARKS")
            narration = _text(narration_el)
            rows.append({
                "date": date_str,
                "voucher_type": voucher_type.strip(),
                "party_name": party_name or _normalize_party(ledger_name),
                "amount": amount,
                "ledger_name": ledger_name.strip(),
                "narration": narration,
                "is_duplicate": False,
            })

    # Duplicate detection: same date + amount + party_name
    seen: set[tuple[str, float, str]] = set()
    for r in rows:
        key = (r["date"], r["amount"], r["party_name"])
        if key in seen:
            r["is_duplicate"] = True
        else:
            seen.add(key)

    return rows


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tally_parser.py <path-to-tally.xml>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    rows = parse_tally_xml(path)
    for i, row in enumerate(rows[:10]):
        print(row)
    if len(rows) > 10:
        print(f"... and {len(rows) - 10} more rows (total {len(rows)})")


if __name__ == "__main__":
    main()
