"""GST: GSTR1, GSTR3B, reconcile 2B, notices, calendar."""
import calendar
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, get_company_for_user
from db.database import get_db
from models import User, Company, GstNotice, GstReturn
from utils.activity import log_activity
from schemas.gst import (
    DraftReplyRequest,
    GstCalendarItem,
    GstComplianceSection,
    GstComplianceSummary,
    GstNoticeCreate,
    GstNoticeResponse,
    MarkGstReturnFiled,
)
from services.gst_calendar import obligations_in_due_range, urgency_status

router = APIRouter(tags=["gst"])


async def _calendar_items(
    company_id: UUID,
    d0: date,
    d1: date,
    db: AsyncSession,
) -> list[GstCalendarItem]:
    obligations = obligations_in_due_range(d0, d1)
    if not obligations:
        return []
    types = {o.return_type for o in obligations}
    periods = {o.period for o in obligations}
    result = await db.execute(
        select(GstReturn).where(
            GstReturn.company_id == company_id,
            GstReturn.return_type.in_(types),
            GstReturn.period.in_(periods),
        )
    )
    rows = result.scalars().all()
    by_key = {(r.return_type, r.period): r for r in rows}
    today = date.today()
    items: list[GstCalendarItem] = []
    for o in obligations:
        r = by_key.get((o.return_type, o.period))
        filed = bool(r and (r.filed_at is not None or r.status == "filed"))
        st = urgency_status(filed=filed, due_date=o.due_date, today=today)
        items.append(
            GstCalendarItem(
                return_type=o.return_type,
                period=o.period,
                due_date=o.due_date.isoformat(),
                title=o.title,
                description=o.description,
                filed=filed,
                status=st,
            )
        )
    return sorted(items, key=lambda x: x.due_date)


@router.get("/{company_id}/gst/calendar", response_model=list[GstCalendarItem])
async def gst_calendar(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
):
    today = date.today()
    d0 = from_date or (today - timedelta(days=7))
    d1 = to_date or (today + timedelta(days=90))
    if d1 < d0:
        raise HTTPException(status_code=400, detail="to must be >= from")
    return await _calendar_items(company.id, d0, d1, db)


@router.get("/{company_id}/gst/compliance-summary", response_model=GstComplianceSummary)
async def gst_compliance_summary(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=6)
    month_start = date(today.year, today.month, 1)
    last_mday = calendar.monthrange(today.year, today.month)[1]
    month_end = date(today.year, today.month, last_mday)

    week_items = await _calendar_items(company.id, week_start, week_end, db)
    month_items = await _calendar_items(company.id, month_start, month_end, db)

    return GstComplianceSummary(
        today=today.isoformat(),
        this_week=GstComplianceSection(
            start=week_start.isoformat(),
            end=week_end.isoformat(),
            items=week_items,
        ),
        this_month=GstComplianceSection(
            start=month_start.isoformat(),
            end=month_end.isoformat(),
            items=month_items,
        ),
    )


@router.post("/{company_id}/gst/returns/mark-filed")
async def mark_gst_return_filed(
    body: MarkGstReturnFiled,
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GstReturn).where(
            GstReturn.company_id == company.id,
            GstReturn.return_type == body.return_type,
            GstReturn.period == body.period,
        )
    )
    row = result.scalar_one_or_none()
    now = datetime.now(timezone.utc)
    if row:
        row.filed_at = now
        row.status = "filed"
    else:
        db.add(
            GstReturn(
                company_id=company.id,
                return_type=body.return_type,
                period=body.period,
                status="filed",
                filed_at=now,
            )
        )
    await log_activity(
        db, company.id, user.id, "GST_RETURN", 
        f"Marked {body.return_type} for {body.period} as filed",
        {"return_type": body.return_type, "period": body.period}
    )
    await db.flush()
    return {"ok": True, "return_type": body.return_type, "period": body.period}


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
    user: User = Depends(get_current_user),
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
    await log_activity(
        db, company.id, user.id, "GST_NOTICE_CREATE",
        f"Created GST Notice reference: {body.notice_ref}",
        {"notice_ref": body.notice_ref, "notice_type": body.notice_type, "notice_id": str(notice.id)}
    )
    await db.flush()
    return GstNoticeResponse.model_validate(notice)


@router.post("/{company_id}/gst/notices/{notice_id}/analyze")
async def analyze_notice(
    notice_id: UUID,
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GstNotice).where(GstNotice.id == notice_id, GstNotice.company_id == company.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Notice not found")
    
    await log_activity(
        db, company.id, user.id, "AI_ANALYSIS",
        f"Ran AI analysis on notice: {notice_id}",
        {"notice_id": str(notice_id)}
    )
    return {"notice_id": str(notice_id), "analysis": "placeholder"}


@router.post("/{company_id}/gst/notices/{notice_id}/draft-reply")
async def draft_reply(
    notice_id: UUID,
    body: DraftReplyRequest,
    company: Company = Depends(get_company_for_user),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(GstNotice).where(GstNotice.id == notice_id, GstNotice.company_id == company.id))
    notice = result.scalar_one_or_none()
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    notice.reply_text = body.reply_text
    await log_activity(
        db, company.id, user.id, "NOTICE_DRAFT",
        f"Generated/Updated draft reply for notice: {notice_id}",
        {"notice_id": str(notice_id)}
    )
    await db.flush()
    return {"notice_id": str(notice_id), "reply_text": body.reply_text}
