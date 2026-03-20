"""Stock groups, stock items, units, godowns, employees."""
from decimal import Decimal
from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric

from db.database import Base
from models.base import TimestampMixin, uuid_default


class StockGroup(Base, TimestampMixin):
    __tablename__ = "stock_groups"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    parent_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("stock_groups.id", ondelete="SET NULL"), nullable=True)


class Unit(Base, TimestampMixin):
    __tablename__ = "units"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_compound: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    base_unit_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("units.id", ondelete="SET NULL"), nullable=True)
    conversion_factor: Mapped[Decimal | None] = mapped_column(Numeric(18, 6), nullable=True)


class StockItem(Base, TimestampMixin):
    __tablename__ = "stock_items"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    group_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("stock_groups.id", ondelete="RESTRICT"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hsn_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    sac_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    gst_rate: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    mrp: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    opening_qty: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False, default=0)
    opening_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, default=0)
    reorder_level: Mapped[Decimal | None] = mapped_column(Numeric(18, 4), nullable=True)
    batch_tracking: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    expiry_tracking: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Godown(Base, TimestampMixin):
    __tablename__ = "godowns"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)


class Employee(Base, TimestampMixin):
    __tablename__ = "employees"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(100), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    aadhaar: Mapped[str | None] = mapped_column(String(12), nullable=True)
    bank_account: Mapped[str | None] = mapped_column(String(50), nullable=True)
    joining_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    salary_structure: Mapped[str | None] = mapped_column(String(50), nullable=True)
