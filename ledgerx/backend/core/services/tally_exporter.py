"""
Tally XML exporter: generate valid Tally XML from LedgerX data.
Export vouchers and ledger masters in TALLYMESSAGE format for import into TallyPrime.
"""
import xml.etree.ElementTree as ET
from decimal import Decimal
from typing import Any
from datetime import datetime


def _escape(s: str) -> str:
    if s is None:
        return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _elem(parent: ET.Element, tag: str, text: str | None = None, tail: str | None = None) -> ET.Element:
    el = ET.SubElement(parent, tag)
    if text is not None:
        el.text = str(text)
    if tail is not None:
        el.tail = tail
    return el


def export_ledgers_to_tally_xml(ledgers: list[dict[str, Any]]) -> str:
    """
    Export ledger masters to Tally XML.
    Each ledger: {name, parent, opening_balance, gstn, ...}
    """
    root = ET.Element("ENVELOPE")
    header = ET.SubElement(root, "HEADER")
    _elem(header, "TALLYREQUEST", "Export Data")
    body = ET.SubElement(root, "BODY")
    import_e = ET.SubElement(body, "IMPORTDATA")
    req = ET.SubElement(import_e, "REQUESTDESC")
    _elem(req, "REPORTNAME", "Ledger Masters")
    reqdata = ET.SubElement(import_e, "REQUESTDATA")
    for led in ledgers:
        msg = ET.SubElement(reqdata, "TALLYMESSAGE")
        led_el = ET.SubElement(msg, "LEDGER", attrib={"NAME": _escape(led.get("name", ""))[:100], "ACTION": "Create"})
        if led.get("parent"):
            _elem(led_el, "PARENT", led["parent"])
        ob = led.get("opening_balance") or 0
        try:
            ob = Decimal(str(ob))
        except Exception:
            ob = Decimal("0")
        _elem(led_el, "OPENINGBALANCE", str(ob))
        if led.get("gstn"):
            _elem(led_el, "GSTN", led["gstn"])
        _elem(led_el, "COUNTRYNAME", led.get("country", "India"))
    return _to_string(root)


def export_vouchers_to_tally_xml(vouchers: list[dict[str, Any]]) -> str:
    """
    Export vouchers to Tally XML. Each voucher: date, voucher_type, number, party_ledger, narration, amount, entries[], inventory_lines[].
    entries: [{ledger_name, dr_amount, cr_amount, narration, bill_ref}]
    """
    root = ET.Element("ENVELOPE")
    header = ET.SubElement(root, "HEADER")
    _elem(header, "TALLYREQUEST", "Export Data")
    body = ET.SubElement(root, "BODY")
    import_e = ET.SubElement(body, "IMPORTDATA")
    req = ET.SubElement(import_e, "REQUESTDESC")
    _elem(req, "REPORTNAME", "Vouchers")
    reqdata = ET.SubElement(import_e, "REQUESTDATA")

    vchtype_tally = {
        "PAYMENT": "Payment",
        "RECEIPT": "Receipt",
        "JOURNAL": "Journal",
        "CONTRA": "Contra",
        "SALES": "Sales",
        "PURCHASE": "Purchase",
        "CREDIT_NOTE": "Credit Note",
        "DEBIT_NOTE": "Debit Note",
        "DELIVERY_NOTE": "Delivery Note",
        "RECEIPT_NOTE": "Receipt Note",
        "STOCK_JOURNAL": "Stock Journal",
        "PHYSICAL_STOCK": "Physical Stock",
        "MEMORANDUM": "Memorandum",
        "REVERSING_JOURNAL": "Reversing Journal",
    }

    for v in vouchers:
        msg = ET.SubElement(reqdata, "TALLYMESSAGE")
        vtype = v.get("voucher_type", "Journal")
        vtype_tally_name = vchtype_tally.get(vtype.upper(), "Journal")
        vou_el = ET.SubElement(msg, "VOUCHER", attrib={"VCHTYPE": vtype_tally_name, "ACTION": "Create"})

        date_val = v.get("date", "")
        if isinstance(date_val, datetime):
            date_val = date_val.strftime("%Y%m%d")
        elif isinstance(date_val, str) and len(date_val) >= 10:
            try:
                dt = datetime.strptime(date_val[:10], "%Y-%m-%d")
                date_val = dt.strftime("%Y%m%d")
            except Exception:
                pass
        _elem(vou_el, "DATE", date_val)

        if v.get("tally_guid"):
            _elem(vou_el, "GUID", v["tally_guid"])
        if v.get("number") or v.get("voucher_number"):
            _elem(vou_el, "VOUCHERNUMBER", v.get("number") or v.get("voucher_number", ""))
        if v.get("party_ledger") or v.get("party_ledger_name"):
            _elem(vou_el, "PARTYLEDGERNAME", v.get("party_ledger") or v.get("party_ledger_name", ""))
        if v.get("narration"):
            _elem(vou_el, "NARRATION", v["narration"])
        amt = v.get("amount")
        if amt is not None:
            _elem(vou_el, "AMOUNT", str(Decimal(str(amt))))

        for e in v.get("entries", []):
            all_el = ET.SubElement(vou_el, "ALLLEDGERENTRIES.LIST")
            _elem(all_el, "LEDGERNAME", e.get("ledger_name", ""))
            dr = Decimal(str(e.get("dr_amount", 0) or 0))
            cr = Decimal(str(e.get("cr_amount", 0) or 0))
            # Tally: positive = Debit, negative = Credit
            if dr > 0:
                _elem(all_el, "AMOUNT", str(dr))
                _elem(all_el, "ISDEEMEDPOSITIVE", "Yes")
            elif cr > 0:
                _elem(all_el, "AMOUNT", "-" + str(cr))
                _elem(all_el, "ISDEEMEDPOSITIVE", "No")
            if e.get("narration"):
                _elem(all_el, "NARRATION", e["narration"])
            if e.get("bill_ref"):
                _elem(all_el, "BILLREF", e["bill_ref"])

        for inv in v.get("inventory_lines", []):
            inv_el = ET.SubElement(vou_el, "ALLINVENTORYENTRIES.LIST")
            _elem(inv_el, "STOCKITEMNAME", inv.get("stock_item", ""))
            _elem(inv_el, "ACTUALQTY", str(Decimal(str(inv.get("quantity", 0) or 0))))
            _elem(inv_el, "RATE", str(Decimal(str(inv.get("rate", 0) or 0))))
            if inv.get("amount") is not None:
                _elem(inv_el, "AMOUNT", str(Decimal(str(inv["amount"]))))

    return _to_string(root)


def _to_string(root: ET.Element) -> str:
    ET.indent(root, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="unicode", method="xml")
