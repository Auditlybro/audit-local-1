"""GST: GSTR1, GSTR3B, reconcile 2B, notices."""
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_company_for_user
from db.database import get_db
from models import Company, GstNotice, GstReturn
from schemas.gst import GstNoticeCreate, GstNoticeResponse, DraftReplyRequest

router = APIRouter(tags=["gst"])


@router.get("/{company_id}/gst/gstr1")
async def get_gstr1(
    period: str = Query(...),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GstReturn).where(
            GstReturn.company_id == company.id,
            GstReturn.return_type == "GSTR1",
            GstReturn.period == period,
        )
    )
    r = result.scalar_one_or_none()
    return {"period": period, "data": r.json_data if r and r.json_data else {}}


@router.get("/{company_id}/gst/gstr3b")
async def get_gstr3b(
    period: str = Query(...),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GstReturn).where(
            GstReturn.company_id == company.id,
            GstReturn.return_type == "GSTR3B",
            GstReturn.period == period,
        )
    )
    r = result.scalar_one_or_none()
    return {"period": period, "data": r.json_data if r and r.json_data else {}}


@router.post("/{company_id}/gst/reconcile-2b")
async def reconcile_2b(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    return {"status": "ok", "message": "Reconciliation placeholder"}


@router.get("/{company_id}/gst/notices")
async def list_gst_notices(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GstNotice).where(GstNotice.company_id == company.id).order_by(GstNotice.created_at.desc()))
    return [GstNoticeResponse.model_validate(n) for n in result.scalars().all()]


@router.post("/{company_id}/gst/notices", status_code=201)
async def create_gst_notice(
    body: GstNoticeCreate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    notice = GstNotice(
        company_id=company.id,
        notice_ref=body.notice_ref,
        notice_type=body.notice_type,
        section=body.section,
        period=body.period,
        amount_demanded=body.amount_demanded,
        deadline=date.fromisoformat(body.deadline) if body.deadline else None,
        notice_text=body.notice_text,
    )
    db.add(notice)
    await db.flush()
    return GstNoticeResponse.model_validate(notice)


@router.post("/{company_id}/gst/notices/{notice_id}/analyze")
async def analyze_notice(
    notice_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GstNotice).where(GstNotice.id == notice_id, GstNotice.company_id == company.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Notice not found")
    return {"notice_id": str(notice_id), "analysis": "placeholder"}


@router.post("/{company_id}/gst/notices/{notice_id}/draft-reply")
async def draft_reply(
    notice_id: UUID,
    body: DraftReplyRequest,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GstNotice).where(GstNotice.id == notice_id, GstNotice.company_id == company.id))
    notice = result.scalar_one_or_none()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    notice.reply_text = body.reply_text
    await db.flush()
    return {"notice_id": str(notice_id), "reply_text": body.reply_text}
