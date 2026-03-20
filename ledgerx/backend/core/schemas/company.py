"""Company schemas."""
from uuid import UUID

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    name: str
    gstin: str | None = None
    pan: str | None = None
    cin: str | None = None
    address: str | None = None
    state_code: str | None = None
    financial_year: str | None = None
    logo_url: str | None = None


class CompanyUpdate(BaseModel):
    name: str | None = None
    gstin: str | None = None
    pan: str | None = None
    cin: str | None = None
    address: str | None = None
    state_code: str | None = None
    financial_year: str | None = None
    logo_url: str | None = None


class CompanyResponse(BaseModel):
    id: UUID
    org_id: UUID
    name: str
    gstin: str | None
    pan: str | None
    cin: str | None
    address: str | None
    state_code: str | None
    financial_year: str | None
    logo_url: str | None

    class Config:
        from_attributes = True
