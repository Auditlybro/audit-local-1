"""Voucher and entry schemas."""
from decimal import Decimal
from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


VOUCHER_TYPES = [
    "PAYMENT", "RECEIPT", "JOURNAL", "CONTRA", "SALES", "PURCHASE",
    "CREDIT_NOTE", "DEBIT_NOTE", "DELIVERY_NOTE", "RECEIPT_NOTE",
    "STOCK_JOURNAL", "PHYSICAL_STOCK", "SALES_ORDER", "PURCHASE_ORDER",
    "PAYROLL", "MEMORANDUM", "REVERSING_JOURNAL",
]


class VoucherEntryInput(BaseModel):
    ledger_id: UUID
    dr_amount: Decimal = 0
    cr_amount: Decimal = 0
    narration: str | None = None
    bill_ref: str | None = None
    cost_centre: str | None = None


class InvoiceItemInput(BaseModel):
    stock_item_id: UUID
    godown_id: UUID | None = None
    batch: str | None = None
    quantity: Decimal
    rate: Decimal
    unit: str | None = None
    discount_pct: Decimal = 0
    discount_amount: Decimal = 0
    taxable_value: Decimal
    cgst_rate: Decimal = 0
    cgst_amount: Decimal = 0
    sgst_rate: Decimal = 0
    sgst_amount: Decimal = 0
    igst_rate: Decimal = 0
    igst_amount: Decimal = 0
    total_amount: Decimal


class VoucherCreate(BaseModel):
    voucher_type: str
    date: date
    party_ledger_id: UUID | None = None
    narration: str | None = None
    reference: str | None = None
    cost_centre: str | None = None
    is_optional: bool = False
    entries: list[VoucherEntryInput]
    invoice_items: list[InvoiceItemInput] | None = None


class VoucherUpdate(BaseModel):
    date: Optional[date] = None
    party_ledger_id: Optional[UUID] = None
    narration: Optional[str] = None
    reference: Optional[str] = None
    cost_centre: Optional[str] = None
    entries: Optional[list[VoucherEntryInput]] = None
    invoice_items: Optional[list[InvoiceItemInput]] = None


class VoucherEntryResponse(BaseModel):
    id: UUID
    ledger_id: UUID
    dr_amount: Decimal
    cr_amount: Decimal
    narration: str | None

    class Config:
        from_attributes = True


class VoucherResponse(BaseModel):
    id: UUID
    company_id: UUID
    voucher_type: str
    number: str | None
    date: date
    party_ledger_id: UUID | None
    narration: str | None
    amount: Decimal | None
    reference: str | None
    is_cancelled: bool
    created_at: str | None
    entries: list[VoucherEntryResponse] = []

    class Config:
        from_attributes = True
