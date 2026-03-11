"""
Audit-Local backend — FastAPI. 100% offline. No cloud, no telemetry.
"""

import os
import sys
from pathlib import Path
from tempfile import NamedTemporaryFile

# Allow importing ai package (repo root) when running from backend/
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from fastapi import FastAPI, File, UploadFile, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from tally_parser import parse_tally_xml
from notice_parser import analyze_notice
from ai.rag_setup import search_law

app = FastAPI(
    title="Audit-Local API",
    description="Backend for Audit-Local desktop app. All data stays local.",
    version="0.1.0",
)

# CORS for localhost only (Tauri dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:5173", "http://127.0.0.1", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Health check for desktop app / process manager."""
    return {"status": "ok", "app": "audit-local"}


@app.post("/parse-tally")
async def parse_tally(file: UploadFile = File(...)):
    """
    Accept a Tally XML file upload, parse vouchers, return JSON array of rows.
    All processing is local; file is not stored after request.
    """
    if not file.filename or not file.filename.lower().endswith(".xml"):
        raise HTTPException(status_code=400, detail="Only .xml files are accepted")
    try:
        contents = await file.read()
        with NamedTemporaryFile(mode="wb", suffix=".xml", delete=False) as tmp:
            tmp.write(contents)
            tmp.flush()
            tmp_path = tmp.name
        try:
            rows = parse_tally_xml(Path(tmp_path))
        finally:
            os.unlink(tmp_path)
        return rows
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Parse error: {e!s}")


class NoticeBody(BaseModel):
    notice_text: str = ""


@app.post("/analyze-notice")
async def analyze_notice_route(body: NoticeBody = Body(...)):
    """
    Accept plain text GST notice, extract notice_type, section_number,
    tax_period, amount_demanded, deadline. Returns JSON. 100% local.
    """
    return analyze_notice(body.notice_text or "")


def _format_amount(amt: str) -> str:
    """Format amount with Indian-style commas (e.g. 221100 -> 2,21,100)."""
    if not amt:
        return ""
    s = amt.replace(",", "").strip()
    try:
        n = int(float(s))
        if n < 0:
            return "-" + _format_amount(str(-n))
        s = str(n)
        if len(s) <= 3:
            return s
        result = s[-3:]
        s = s[:-3]
        while s:
            result = s[-2:] + "," + result
            s = s[:-2]
        return result
    except ValueError:
        return amt


def _build_draft_reply(notice_summary: dict, relevant_sections: list[dict]) -> str:
    """Build structured draft reply with specific amounts and sections. No cloud."""
    section_x = notice_summary.get("section_number") or "X"
    date_placeholder = "the date of the notice"
    if notice_summary.get("deadline"):
        date_placeholder = notice_summary["deadline"]
    amount_str = notice_summary.get("amount_demanded") or ""
    amount_fmt = f" ₹{_format_amount(amount_str)}" if amount_str else ""
    sections_cited = [f"Section {section_x}"] if (section_x and section_x != "X") else []
    for s in relevant_sections:
        sid = s.get("section_id")
        if not sid:
            continue
        if section_x and section_x != "X" and (section_x in sid or sid.endswith(section_x)):
            continue
        if sid not in sections_cited:
            sections_cited.append(sid)
    sections_phrase = ", ".join(sections_cited) if sections_cited else f"Section {section_x}"
    ref_section = relevant_sections[0].get("section_id") if relevant_sections else f"Section {section_x}"
    itc_argument = (
        f"The ITC difference of{amount_fmt} is attributable to timing differences in vendor invoice "
        "uploads to GSTR-2B, which do not constitute ineligible credit under Section 16(4)."
    )
    if not amount_str:
        itc_argument = (
            "The ITC difference referred to in the notice is attributable to timing differences in "
            "vendor invoice uploads to GSTR-2B, which do not constitute ineligible credit under Section 16(4)."
        )
    docs = "Copies of relevant invoices, GSTR-2B, returns, and supporting records as applicable."
    return (
        f"In response to your notice dated {date_placeholder} under Section {section_x},\n\n"
        f"The notice cites {sections_phrase} of the CGST Act / Rules. As per {ref_section} and Rule 36(4),\n\n"
        f"We submit that {itc_argument}\n\n"
        f"Enclosed: {docs}\n\n"
        "We request a personal hearing before any demand is confirmed under Section 73(9)."
    )


@app.post("/draft-reply")
async def draft_reply(body: NoticeBody = Body(...)):
    """
    Analyze notice, retrieve relevant law sections from local RAG, and return
    a structured draft reply. 100% local; no cloud or external APIs.
    """
    notice_text = (body.notice_text or "").strip()
    if not notice_text:
        return {
            "notice_summary": {},
            "relevant_sections": [],
            "draft_reply": "",
        }
    notice_summary = analyze_notice(notice_text)
    query = f"{notice_summary.get('notice_type', '')} {notice_summary.get('section_number', '')}".strip() or notice_text[:200]
    relevant_sections = search_law(query, top_k=3)
    draft_reply = _build_draft_reply(notice_summary, relevant_sections)
    return {
        "notice_summary": notice_summary,
        "relevant_sections": relevant_sections,
        "draft_reply": draft_reply,
    }
