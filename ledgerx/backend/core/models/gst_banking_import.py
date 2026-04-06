"""GST, banking, import_sessions."""
from decimal import Decimal
from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from db.database import Base
from models.base import TimestampMixin, uuid_default


class GstReturn(Base, TimestampMixin):
    __tablename__ = "gst_returns"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    return_type: Mapped[str] = mapped_column(String(20), nullable=False)
    period: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    json_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


class Einvoice(Base, TimestampMixin):
    __tablename__ = "einvoices"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    voucher_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)
    irn: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ack_no: Mapped[str | None] = mapped_column(String(100), nullable=True)
    ack_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    qr_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class Ewaybill(Base, TimestampMixin):
    __tablename__ = "ewaybills"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    voucher_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vouchers.id", ondelete="CASCADE"), nullable=False)
    ewb_no: Mapped[str | None] = mapped_column(String(50), nullable=True)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    valid_till: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")


class GstNotice(Base, TimestampMixin):
    __tablename__ = "gst_notices"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    notice_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notice_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    section: Mapped[str | None] = mapped_column(String(50), nullable=True)
    period: Mapped[str | None] = mapped_column(String(20), nullable=True)
    amount_demanded: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    deadline: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="open")
    notice_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    reply_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class BankAccount(Base, TimestampMixin):
    __tablename__ = "bank_accounts"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    ledger_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ledgers.id", ondelete="CASCADE"), nullable=False, unique=True)
    account_number: Mapped[str] = mapped_column(String(50), nullable=False)
    ifsc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    bank_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    branch: Mapped[str | None] = mapped_column(String(255), nullable=True)
    account_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    reconciled_till: Mapped[date | None] = mapped_column(Date, nullable=True)
    transactions: Mapped[list["BankTransaction"]] = relationship("BankTransaction", back_populates="bank_account", cascade="all, delete-orphan")


class BankTransaction(Base, TimestampMixin):
    __tablename__ = "bank_transactions"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    bank_account_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("bank_accounts.id", ondelete="CASCADE"), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    value_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    balance: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    reconciled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    voucher_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vouchers.id", ondelete="SET NULL"), nullable=True)
    imported_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    bank_account: Mapped["BankAccount"] = relationship("BankAccount", back_populates="transactions")


class ImportSession(Base, TimestampMixin):
    __tablename__ = "import_sessions"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    total_records: Mapped[int] = mapped_column(Integer, default=0)
    imported_records: Mapped[int] = mapped_column(Integer, default=0)
    error_records: Mapped[int] = mapped_column(Integer, default=0)
    errors_json: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
