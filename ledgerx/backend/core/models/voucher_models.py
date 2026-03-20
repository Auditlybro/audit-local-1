"""Vouchers, voucher_entries, invoice_items."""
from decimal import Decimal
from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from db.database import Base
from models.base import TimestampMixin, uuid_default


class Voucher(Base, TimestampMixin):
    __tablename__ = "vouchers"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    voucher_type: Mapped[str] = mapped_column(String(50), nullable=False)
    number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    party_ledger_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="SET NULL"), nullable=True)
    narration: Mapped[str | None] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cost_centre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_optional: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_cancelled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_by: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    tally_guid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")
    entries: Mapped[list["VoucherEntry"]] = relationship("VoucherEntry", back_populates="voucher", cascade="all, delete-orphan")
    invoice_items: Mapped[list["InvoiceItem"]] = relationship("InvoiceItem", back_populates="voucher", cascade="all, delete-orphan")


class VoucherEntry(Base, TimestampMixin):
    __tablename__ = "voucher_entries"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    voucher_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)
    ledger_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="RESTRICT"), nullable=False)
    dr_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    cr_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    narration: Mapped[str | None] = mapped_column(Text, nullable=True)
    bill_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cost_centre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    voucher: Mapped["Voucher"] = relationship("Voucher", back_populates="entries")


class InvoiceItem(Base, TimestampMixin):
    __tablename__ = "invoice_items"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    voucher_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)
    stock_item_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("stock_items.id", ondelete="SET NULL"), nullable=True)
    godown_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("godowns.id", ondelete="SET NULL"), nullable=True)
    batch: Mapped[str | None] = mapped_column(String(100), nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    rate: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    discount_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    taxable_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    cgst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    sgst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    igst_rate: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    voucher: Mapped["Voucher"] = relationship("Voucher", back_populates="invoice_items")
