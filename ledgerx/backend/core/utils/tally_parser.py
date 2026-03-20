"""
Tally XML parser: TALLYMESSAGE > LEDGER (masters) and VOUCHER (transactions).
Handles Tally convention: negative amount = Credit, positive = Debit.
24 voucher types from VCHTYPE. GUID duplicate detection. Bill refs, GST from ledger names.
"""
import xml.etree.ElementTree as ET
import re
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any
from datetime import datetime

# Map Tally VCHTYPE to LedgerX voucher types (24 types)
VCHTYPE_MAP = {
    "Payment": "PAYMENT",
    "Receipt": "RECEIPT",
    "Journal": "JOURNAL",
    "Contra": "CONTRA",
    "Sales": "SALES",
    "Purchase": "PURCHASE",
    "Credit Note": "CREDIT_NOTE",
    "Debit Note": "DEBIT_NOTE",
    "Delivery Note": "DELIVERY_NOTE",
    "Receipt Note": "RECEIPT_NOTE",
    "Stock Journal": "STOCK_JOURNAL",
    "Physical Stock": "PHYSICAL_STOCK",
    "Sales Order": "SALES_ORDER",
    "Purchase Order": "PURCHASE_ORDER",
    "Payroll": "PAYROLL",
    "Memorandum": "MEMORANDUM",
    "Reversing Journal": "REVERSING_JOURNAL",
    "Material In": "RECEIPT_NOTE",
    "Material Out": "DELIVERY_NOTE",
    "Journal Voucher": "JOURNAL",
    "Payment Voucher": "PAYMENT",
    "Receipt Voucher": "RECEIPT",
    "Contra Voucher": "CONTRA",
    "Sales Voucher": "SALES",
    "Purchase Voucher": "PURCHASE",
}


@dataclass
class TallyLedgerMaster:
    """Parsed ledger master from Tally XML."""
    name: str
    parent: str = ""
    opening_balance: Decimal = Decimal("0")
    gstn: str = ""
    country: str = "India"
    action: str = "Create"


@dataclass
class TallyEntry:
    """Single ledger line (debit or credit). Tally: negative amount = Credit."""
    ledger_name: str
    dr_amount: Decimal
    cr_amount: Decimal
    narration: str = ""
    cost_centre: str = ""
    bill_ref: str = ""
    gst_type: str = ""  # CGST/SGST/IGST from ledger name


@dataclass
class TallyVoucher:
    """Normalized voucher from Tally XML."""
    voucher_type: str
    date: str
    narration: str = ""
    reference: str = ""
    voucher_number: str = ""
    party_ledger: str = ""
    amount: Decimal = Decimal("0")
    entries: list[TallyEntry] = field(default_factory=list)
    tally_guid: str = ""
    inventory_lines: list[dict[str, Any]] = field(default_factory=list)


def _text(el: ET.Element | None, default: str = "") -> str:
    if el is None:
        return default
    return (el.text or "").strip()


def _attr(el: ET.Element | None, key: str, default: str = "") -> str:
    if el is None:
        return default
    return (el.get(key) or default).strip()


def _decimal(el: ET.Element | None) -> Decimal:
    if el is None or el.text is None:
        return Decimal("0")
    try:
        s = el.text.strip().replace(",", "")
        return Decimal(s)
    except Exception:
        return Decimal("0")


def _find_all(parent: ET.Element, path: str) -> list[ET.Element]:
    return parent.findall(path) or []


def _find_one(parent: ET.Element, path: str) -> ET.Element | None:
    return parent.find(path)


def _normalize_date(date_str: str) -> str:
    if not date_str:
        return datetime.now().strftime("%Y-%m-%d")
    date_str = date_str.strip()
    try:
        if len(date_str) == 8 and date_str.isdigit():
            return datetime.strptime(date_str, "%Y%m%d").strftime("%Y-%m-%d")
        if "T" in date_str or "-" in date_str:
            return datetime.fromisoformat(date_str.replace(" ", "T")[:10]).strftime("%Y-%m-%d")
        # DD-MMM-YYYY or similar
        for fmt in ("%d-%b-%Y", "%d/%m/%Y", "%Y-%m-%d"):
            try:
                return datetime.strptime(date_str[:10], fmt).strftime("%Y-%m-%d")
            except ValueError:
                continue
    except Exception:
        pass
    return date_str


def _gst_type_from_ledger_name(name: str) -> str:
    n = (name or "").upper()
    if "CGST" in n:
        return "CGST"
    if "SGST" in n:
        return "SGST"
    if "IGST" in n:
        return "IGST"
    return ""


def parse_tally_masters(content: str | bytes) -> list[TallyLedgerMaster]:
    """
    Parse TALLYMESSAGE > LEDGER for masters import.
    <LEDGER NAME="..." ACTION="Create">
      <PARENT>...</PARENT>
      <OPENINGBALANCE>...</OPENINGBALANCE>
      <GSTN>...</GSTN>
      <COUNTRYNAME>...</COUNTRYNAME>
    </LEDGER>
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    root = ET.fromstring(content)
    messages = root.findall(".//TALLYMESSAGE") or root.findall("TALLYMESSAGE") or ([root] if root.tag == "TALLYMESSAGE" else [])
    masters: list[TallyLedgerMaster] = []
    for msg in messages:
        for led_el in _find_all(msg, "LEDGER"):
            name = _attr(led_el, "NAME") or _text(_find_one(led_el, "NAME"))
            parent = _text(_find_one(led_el, "PARENT"))
            opening = _decimal(_find_one(led_el, "OPENINGBALANCE"))
            gstn = _text(_find_one(led_el, "GSTN"))
            country = _text(_find_one(led_el, "COUNTRYNAME")) or "India"
            action = _attr(led_el, "ACTION", "Create")
            if name:
                masters.append(TallyLedgerMaster(name=name, parent=parent, opening_balance=opening, gstn=gstn, country=country, action=action))
    return masters


def parse_tally_xml(content: str | bytes) -> list[TallyVoucher]:
    """
    Parse TALLYMESSAGE > VOUCHER. Handles:
    - VCHTYPE (map to 24 types)
    - DATE, GUID, VOUCHERNUMBER, PARTYLEDGERNAME, NARRATION, AMOUNT
    - ALLLEDGERENTRIES.LIST: LEDGERNAME, AMOUNT (negative=Credit), BILLALLOCATIONS.LIST
    - ALLINVENTORYENTRIES.LIST: STOCKITEMNAME, ACTUALQTY, RATE, AMOUNT
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    root = ET.fromstring(content)
    messages = root.findall(".//TALLYMESSAGE") or root.findall("TALLYMESSAGE") or ([root] if root.tag == "TALLYMESSAGE" else [])
    vouchers: list[TallyVoucher] = []
    for msg in messages:
        for v_el in _find_all(msg, "VOUCHER"):
            v = _parse_one_voucher(v_el)
            if v:
                vouchers.append(v)
    return vouchers


def _parse_one_voucher(v_el: ET.Element) -> TallyVoucher | None:
    vchtype = _text(_find_one(v_el, "VCHTYPE")) or _text(_find_one(v_el, "VOUCHERTYPENAME")) or _text(_find_one(v_el, "VOUCHERTYPE"))
    vchtype = (vchtype or "Journal").strip()
    voucher_type = VCHTYPE_MAP.get(vchtype) or "JOURNAL"
    if not voucher_type:
        voucher_type = "JOURNAL"

    date_str = _text(_find_one(v_el, "DATE"))
    date_str = _normalize_date(date_str)

    guid = _text(_find_one(v_el, "GUID"))
    voucher_number = _text(_find_one(v_el, "VOUCHERNUMBER"))
    party_ledger = _text(_find_one(v_el, "PARTYLEDGERNAME")) or _text(_find_one(v_el, "PARTYNAME"))
    narration = _text(_find_one(v_el, "NARRATION"))
    amount = _decimal(_find_one(v_el, "AMOUNT"))

    entries: list[TallyEntry] = []
    for al in _find_all(v_el, "ALLLEDGERENTRIES.LIST"):
        led_name = _text(_find_one(al, "LEDGERNAME")) or _text(_find_one(al, "LEDGER"))
        amt_el = _find_one(al, "AMOUNT")
        amt = _decimal(amt_el)
        # Tally: negative amount = Credit, positive = Debit (standard export)
        if amt >= 0:
            dr, cr = amt, Decimal("0")
        else:
            dr, cr = Decimal("0"), abs(amt)
        # Some exports use ISDEEMEDPOSITIVE: Yes = Debit side
        is_pos = _text(_find_one(al, "ISDEEMEDPOSITIVE"))
        if is_pos == "Yes" and amt != 0:
            dr, cr = amt, Decimal("0")
        elif is_pos == "No" and amt != 0:
            dr, cr = Decimal("0"), abs(amt)
        # Fallback: separate DEBIT/CREDIT elements
        if dr == 0 and cr == 0:
            dr = _decimal(_find_one(al, "DEBIT"))
            cr = _decimal(_find_one(al, "CREDIT"))

        bill_ref = _text(_find_one(al, "BILLREF"))
        for bill in _find_all(al, "BILLALLOCATIONS.LIST"):
            ref = _text(_find_one(bill, "BILLREFERENCE")) or _text(_find_one(bill, "NAME"))
            if ref:
                bill_ref = ref
                break
        cost_centre = _text(_find_one(al, "COSTCENTREALLOCATIONS.LIST/NAME")) or _text(_find_one(al, "COSTCENTRE"))
        ent_narr = _text(_find_one(al, "NARRATION"))
        gst_type = _gst_type_from_ledger_name(led_name)

        if led_name:
            entries.append(TallyEntry(
                ledger_name=led_name,
                dr_amount=dr,
                cr_amount=cr,
                narration=ent_narr,
                cost_centre=cost_centre,
                bill_ref=bill_ref,
                gst_type=gst_type,
            ))

    inv_lines: list[dict[str, Any]] = []
    for il in _find_all(v_el, "ALLINVENTORYENTRIES.LIST"):
        item = _text(_find_one(il, "STOCKITEMNAME")) or _text(_find_one(il, "ITEM"))
        qty = _decimal(_find_one(il, "ACTUALQTY")) or _decimal(_find_one(il, "QUANTITY"))
        rate = _decimal(_find_one(il, "RATE")) or _decimal(_find_one(il, "PRICE"))
        amt = _decimal(_find_one(il, "AMOUNT"))
        inv_lines.append({"stock_item": item, "quantity": qty, "rate": rate, "amount": amt})

    return TallyVoucher(
        voucher_type=voucher_type,
        date=date_str,
        narration=narration,
        reference=voucher_number or guid,
        voucher_number=voucher_number,
        party_ledger=party_ledger,
        amount=amount,
        entries=entries,
        tally_guid=guid,
        inventory_lines=inv_lines,
    )


def detect_duplicates_by_guid(vouchers: list[TallyVoucher], existing_guids: set[str] | None = None) -> list[tuple[int, str]]:
    """Returns list of (index, guid) for vouchers that are duplicates (guid already seen or in existing_guids)."""
    existing = set(existing_guids) if existing_guids else set()
    duplicates: list[tuple[int, str]] = []
    for i, v in enumerate(vouchers):
        if v.tally_guid and v.tally_guid in existing:
            duplicates.append((i, v.tally_guid))
        if v.tally_guid:
            existing.add(v.tally_guid)
    return duplicates
