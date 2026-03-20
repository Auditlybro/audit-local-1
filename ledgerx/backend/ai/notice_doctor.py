"""
Notice Doctor: parse GST notice, ChromaDB similarity search on law corpus, draft legally-cited reply.
Input: notice_text (string).
Output: { notice_summary, relevant_sections, draft_reply, confidence_score 0-100 }.
"""
import re
from typing import Any


def extract_notice_metadata(notice_text: str) -> dict[str, Any]:
    """Extract: type, section, period, amount_demanded, deadline, gstin, notice_reference."""
    text = (notice_text or "").strip()
    out = {
        "type": "",
        "section": "",
        "period": "",
        "amount_demanded": "",
        "deadline": "",
        "gstin": "",
        "notice_reference": "",
    }
    # GSTIN: 15 alphanumeric
    gstin_m = re.search(r"\b\d{2}[A-Z]{5}\d{4}[A-Z]\d[A-Z]\d{4}[A-Z]\b", text, re.I)
    if gstin_m:
        out["gstin"] = gstin_m.group(0).upper()
    # Section
    sec_m = re.search(r"[Ss]ection\s*(\d+[A-Za-z]?(?:\s*\(\d+\))?)", text)
    if sec_m:
        out["section"] = sec_m.group(1).strip()
    sec_m2 = re.search(r"\b(?:Section\s+)?(\d{2,3})\s+of\s+CGST", text, re.I)
    if sec_m2:
        out["section"] = out["section"] or sec_m2.group(1)
    # Amount
    amt_m = re.search(r"[Rr]s\.?\s*([\d,]+(?:\.\d{2})?)", text)
    if amt_m:
        out["amount_demanded"] = amt_m.group(1).replace(",", "")
    amt_m2 = re.search(r"[Ii]n\s+the\s+sum\s+of\s+([\d,]+)", text, re.I)
    if amt_m2:
        out["amount_demanded"] = out["amount_demanded"] or amt_m2.group(1).replace(",", "")
    # Period
    period_m = re.search(r"(?:period|month|year)\s*[:\s]+(\w+\s+\d{4}|\d{2}/\d{4})", text, re.I)
    if period_m:
        out["period"] = period_m.group(1).strip()
    # Deadline
    date_m = re.search(r"(?:within|by|before|date)\s+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})", text, re.I)
    if date_m:
        out["deadline"] = date_m.group(1).strip()
    # Notice ref
    ref_m = re.search(r"(?:Notice\s+[Nn]o\.?|Ref\.?|Reference)\s*[:\s]*([A-Z0-9/-]+)", text)
    if ref_m:
        out["notice_reference"] = ref_m.group(1).strip()
    # Type
    if "ITC" in text or "input tax" in text.lower() or "GSTR-2B" in text or "16(4)" in text:
        out["type"] = "ITC mismatch"
    elif "GSTR-1" in text or "outward supply" in text.lower():
        out["type"] = "GSTR-1 / outward supply"
    elif "demand" in text.lower() or "recovery" in text.lower():
        out["type"] = "Demand / Recovery"
    elif "section 73" in text.lower() or "section 74" in text.lower():
        out["type"] = "Demand (73/74)"
    else:
        out["type"] = "General"
    return out


def search_gst_corpus(query: str, top_k: int = 5) -> list[dict]:
    """ChromaDB similarity search on GST law corpus. Fallback to empty if Chroma not available."""
    try:
        from .rag_setup import search_law
        return search_law(query, top_k=top_k)
    except Exception:
        try:
            from ai.rag_setup import search_law
            return search_law(query, top_k=top_k)
        except Exception:
            return []


def build_draft_reply(
    notice_summary: dict,
    relevant_sections: list[dict],
) -> str:
    """Template: Opening → Citation of sections → Factual submission → Documents list → Prayer → Closing."""
    section_x = notice_summary.get("section") or "X"
    deadline = notice_summary.get("deadline") or "the date specified in the notice"
    amount = notice_summary.get("amount_demanded")
    amount_phrase = f" ₹{amount}" if amount else ""
    sections_cited = [section_x]
    for s in relevant_sections:
        sid = (s.get("section_id") or s.get("id") or "").strip()
        if sid and sid not in sections_cited:
            sections_cited.append(sid)
    sections_text = ", ".join(sections_cited)
    opening = (
        f"With reference to the notice bearing reference {notice_summary.get('notice_reference') or 'as above'} "
        f"under Section {section_x} of the CGST Act, 2017, we submit as under:\n\n"
    )
    citation = (
        f"The notice cites {sections_text} of the CGST Act / Rules. "
        "In this regard we rely on the statutory provisions and the following submissions.\n\n"
    )
    factual = (
        f"The amount of{amount_phrase} referred to in the notice is disputed. "
        "The variance is attributable to timing differences in reporting and/or eligible ITC under Section 16. "
        "We have maintained all records as required under the Act and Rules.\n\n"
    )
    if not amount:
        factual = (
            "The issues raised in the notice are attributable to timing/classification differences "
            "and do not constitute a short payment of tax. We have maintained all records as required.\n\n"
        )
    documents = (
        "Documents enclosed: Copies of relevant returns (GSTR-1, GSTR-3B, GSTR-2B), "
        "invoices, and any other supporting records as applicable.\n\n"
    )
    prayer = (
        "We request that the notice may be dropped or, in the alternative, "
        "a personal hearing be granted before any demand is confirmed under Section 73(9) / 74(9) of the CGST Act.\n\n"
    )
    closing = "Thanking you,\n[Authorised Signatory]"
    return opening + citation + factual + documents + prayer + closing


def run_notice_doctor(notice_text: str) -> dict[str, Any]:
    """
    Step 1: Extract metadata.
    Step 2: ChromaDB search on GST corpus.
    Step 3: Draft reply with template.
    Returns: { notice_summary, relevant_sections, draft_reply, confidence_score 0-100 }.
    """
    notice_text = (notice_text or "").strip()
    if not notice_text:
        return {
            "notice_summary": {},
            "relevant_sections": [],
            "draft_reply": "",
            "confidence_score": 0,
        }
    notice_summary = extract_notice_metadata(notice_text)
    query = f"{notice_summary.get('type', '')} {notice_summary.get('section', '')} CGST".strip() or notice_text[:200]
    relevant_sections = search_gst_corpus(query, top_k=5)
    draft_reply = build_draft_reply(notice_summary, relevant_sections)
    # Confidence: higher if we found section, amount, and law hits
    confidence = 40
    if notice_summary.get("section"):
        confidence += 20
    if notice_summary.get("amount_demanded"):
        confidence += 15
    if notice_summary.get("gstin"):
        confidence += 10
    if relevant_sections:
        confidence += min(15, len(relevant_sections) * 5)
    return {
        "notice_summary": notice_summary,
        "relevant_sections": relevant_sections,
        "draft_reply": draft_reply,
        "confidence_score": min(100, confidence),
    }
