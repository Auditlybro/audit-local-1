"""Ledger groups and ledgers."""
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from db.database import Base
from models.base import TimestampMixin, uuid_default


class LedgerGroup(Base, TimestampMixin):
    __tablename__ = "ledger_groups"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ledger_groups.id", ondelete="SET NULL"), nullable=True)
    nature: Mapped[str] = mapped_column(String(20), nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    tally_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent: Mapped["LedgerGroup | None"] = relationship("LedgerGroup", remote_side=[id], back_populates="children")
    children: Mapped[list["LedgerGroup"]] = relationship("LedgerGroup", back_populates="parent")
    ledgers: Mapped[list["Ledger"]] = relationship("Ledger", back_populates="group")


class Ledger(Base, TimestampMixin):
    __tablename__ = "ledgers"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    group_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("ledger_groups.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    alias: Mapped[str | None] = mapped_column(String(255), nullable=True)
    opening_balance: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    credit_limit: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    tds_applicable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    bank_account_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ifsc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    group: Mapped["LedgerGroup"] = relationship("LedgerGroup", back_populates="ledgers")
