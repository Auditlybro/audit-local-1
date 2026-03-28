"""Organization, User, OrgUser, Company."""
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.database import Base
from models.base import TimestampMixin, uuid_default


class Organization(Base, TimestampMixin):
    __tablename__ = "organizations"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    financial_year_start: Mapped[int] = mapped_column(Integer, nullable=False, default=4)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="INR")
    plan: Mapped[str] = mapped_column(String(50), nullable=False, default="free")


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="user")
    org_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="SET NULL"), nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # relationships
    org: Mapped["Organization | None"] = relationship("Organization", backref="users")



class OrgUser(Base):
    __tablename__ = "org_users"
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="member")
    permissions: Mapped[dict | list] = mapped_column(JSONB, default=list)


class Company(Base, TimestampMixin):
    __tablename__ = "companies"
    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid_default)
    org_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    gstin: Mapped[str | None] = mapped_column(String(15), nullable=True)
    pan: Mapped[str | None] = mapped_column(String(10), nullable=True)
    cin: Mapped[str | None] = mapped_column(String(21), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    state_code: Mapped[str | None] = mapped_column(String(2), nullable=True)
    financial_year: Mapped[str | None] = mapped_column(String(9), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    org: Mapped["Organization"] = relationship("Organization", backref="companies")
