"""Stock item and related schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class StockItemCreate(BaseModel):
    group_id: UUID
    name: str
    hsn_code: str | None = None
    sac_code: str | None = None
    unit: str | None = None
    gst_rate: Decimal | None = None
    mrp: Decimal | None = None
    opening_qty: Decimal = 0
    opening_value: Decimal = 0
    reorder_level: Decimal | None = None
    batch_tracking: bool = False
    expiry_tracking: bool = False


class StockItemUpdate(BaseModel):
    group_id: UUID | None = None
    name: str | None = None
    hsn_code: str | None = None
    sac_code: str | None = None
    unit: str | None = None
    gst_rate: Decimal | None = None
    mrp: Decimal | None = None
    reorder_level: Decimal | None = None
    batch_tracking: bool | None = None
    expiry_tracking: bool | None = None


class StockItemResponse(BaseModel):
    id: UUID
    company_id: UUID
    group_id: UUID
    name: str
    hsn_code: str | None
    unit: str | None
    gst_rate: Decimal | None
    mrp: Decimal | None
    opening_qty: Decimal
    opening_value: Decimal
    reorder_level: Decimal | None

    class Config:
        from_attributes = True


class StockSummaryItem(BaseModel):
    item_id: UUID
    name: str
    quantity: Decimal
    value: Decimal
    unit: str | None


class StockMovementItem(BaseModel):
    date: str
    voucher_type: str
    voucher_id: UUID
    in_qty: Decimal
    out_qty: Decimal
    balance: Decimal
