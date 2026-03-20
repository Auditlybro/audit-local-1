"""Exports: Tally XML, Excel, PDF, GST JSON."""
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
import io

from auth.dependencies import get_company_for_user
from db.database import get_db
from models import Company
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(tags=["exports"])


@router.get("/{company_id}/export/tally-xml")
async def export_tally_xml(
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    # Placeholder: build TALLYMESSAGE > VOUCHER XML from vouchers in date range
    xml = '<?xml version="1.0"?><DATA><TALLYMESSAGE></TALLYMESSAGE></DATA>'
    return StreamingResponse(io.BytesIO(xml.encode("utf-8")), media_type="application/xml", headers={"Content-Disposition": "attachment; filename=ledgerx_export.xml"})


@router.get("/{company_id}/export/excel")
async def export_excel(
    report: str = Query(...),
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
):
    # Placeholder
    buf = io.BytesIO(b"")
    return StreamingResponse(buf, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", headers={"Content-Disposition": "attachment; filename=report.xlsx"})


@router.get("/{company_id}/export/pdf")
async def export_pdf(
    report: str = Query(...),
    from_date: str = Query(..., alias="from"),
    to_date: str = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
):
    # Placeholder
    buf = io.BytesIO(b"")
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=report.pdf"})


@router.get("/{company_id}/export/gst-json")
async def export_gst_json(
    return_type: str = Query(..., alias="return"),
    period: str = Query(...),
    company: Company = Depends(get_company_for_user),
):
    return {"return": return_type, "period": period, "data": {}}
