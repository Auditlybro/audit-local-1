"""GST schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class Gstr1Response(BaseModel):
    period: str
    data: dict


class Gstr3bResponse(BaseModel):
    period: str
    data: dict


class Reconcile2bRequest(BaseModel):
    period: str
    gstr2b_data: dict


class GstNoticeCreate(BaseModel):
    notice_ref: str | None = None
    notice_type: str | None = None
    section: str | None = None
    period: str | None = None
    amount_demanded: Decimal | None = None
    deadline: str | None = None
    notice_text: str | None = None


class GstNoticeResponse(BaseModel):
    id: UUID
    company_id: UUID
    notice_ref: str | None
    notice_type: str | None
    section: str | None
    period: str | None
    amount_demanded: Decimal | None
    deadline: str | None
    status: str
    notice_text: str | None
    reply_text: str | None

    class Config:
        from_attributes = True


class DraftReplyRequest(BaseModel):
    reply_text: str


class GstCalendarItem(BaseModel):
    return_type: str
    period: str
    due_date: str
    title: str
    description: str
    filed: bool
    status: str  # green | amber | red


class GstComplianceSection(BaseModel):
    start: str
    end: str
    items: list[GstCalendarItem]


class GstComplianceSummary(BaseModel):
    today: str
    this_week: GstComplianceSection
    this_month: GstComplianceSection


class MarkGstReturnFiled(BaseModel):
    return_type: str
    period: str
