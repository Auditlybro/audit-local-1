"""Ledger and ledger group schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class LedgerGroupResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    parent_id: UUID | None
    nature: str
    is_system: bool
    tally_name: str | None

    class Config:
        from_attributes = True


class LedgerCreate(BaseModel):
    group_id: UUID
    name: str
    alias: str | None = None
    opening_balance: Decimal = 0
    gstin: str | None = None
    pan: str | None = None
    credit_limit: Decimal | None = None
    tds_applicable: bool = False
    bank_account_number: str | None = None
    ifsc: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    state_code: str | None = None


class LedgerUpdate(BaseModel):
    group_id: UUID | None = None
    name: str | None = None
    alias: str | None = None
    opening_balance: Decimal | None = None
    gstin: str | None = None
    pan: str | None = None
    credit_limit: Decimal | None = None
    tds_applicable: bool | None = None
    bank_account_number: str | None = None
    ifsc: str | None = None
    contact_person: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    state_code: str | None = None


class LedgerResponse(BaseModel):
    id: UUID
    company_id: UUID
    group_id: UUID
    name: str
    alias: str | None
    opening_balance: Decimal
    gstin: str | None
    pan: str | None
    credit_limit: Decimal | None
    state_code: str | None

    class Config:
        from_attributes = True
