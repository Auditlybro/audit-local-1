"""Ledger groups and ledgers CRUD + search."""
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, get_company_for_user
from db.database import get_db
from models import User, Company, LedgerGroup, Ledger
from schemas.ledger import LedgerGroupResponse, LedgerCreate, LedgerUpdate, LedgerResponse

router = APIRouter(tags=["ledgers"])


@router.get("/{company_id}/ledger-groups", response_model=list[LedgerGroupResponse])
async def list_ledger_groups(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LedgerGroup).where(LedgerGroup.company_id == company.id).order_by(LedgerGroup.name)
    )
    return [LedgerGroupResponse.model_validate(g) for g in result.scalars().all()]


@router.get("/{company_id}/ledgers", response_model=list[LedgerResponse])
async def list_ledgers(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Ledger).where(Ledger.company_id == company.id).order_by(Ledger.name))
    return [LedgerResponse.model_validate(l) for l in result.scalars().all()]


@router.post("/{company_id}/ledgers", response_model=LedgerResponse, status_code=201)
async def create_ledger(
    body: LedgerCreate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    ledger = Ledger(
        company_id=company.id,
        group_id=body.group_id,
        name=body.name,
        alias=body.alias,
        opening_balance=body.opening_balance,
        gstin=body.gstin,
        pan=body.pan,
        credit_limit=body.credit_limit,
        tds_applicable=body.tds_applicable,
        bank_account_number=body.bank_account_number,
        ifsc=body.ifsc,
        contact_person=body.contact_person,
        phone=body.phone,
        email=body.email,
        address=body.address,
        state_code=body.state_code,
    )
    db.add(ledger)
    await db.flush()
    return LedgerResponse.model_validate(ledger)


@router.put("/{company_id}/ledgers/{ledger_id}", response_model=LedgerResponse)
async def update_ledger(
    ledger_id: UUID,
    body: LedgerUpdate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Ledger).where(Ledger.id == ledger_id, Ledger.company_id == company.id))
    ledger = result.scalar_one_or_none()
    if not ledger:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ledger not found")
    if body.group_id is not None:
        ledger.group_id = body.group_id
    if body.name is not None:
        ledger.name = body.name
    if body.alias is not None:
        ledger.alias = body.alias
    if body.opening_balance is not None:
        ledger.opening_balance = body.opening_balance
    if body.gstin is not None:
        ledger.gstin = body.gstin
    if body.pan is not None:
        ledger.pan = body.pan
    if body.credit_limit is not None:
        ledger.credit_limit = body.credit_limit
    if body.tds_applicable is not None:
        ledger.tds_applicable = body.tds_applicable
    if body.bank_account_number is not None:
        ledger.bank_account_number = body.bank_account_number
    if body.ifsc is not None:
        ledger.ifsc = body.ifsc
    if body.contact_person is not None:
        ledger.contact_person = body.contact_person
    if body.phone is not None:
        ledger.phone = body.phone
    if body.email is not None:
        ledger.email = body.email
    if body.address is not None:
        ledger.address = body.address
    if body.state_code is not None:
        ledger.state_code = body.state_code
    await db.flush()
    return LedgerResponse.model_validate(ledger)


@router.delete("/{company_id}/ledgers/{ledger_id}", status_code=204)
async def delete_ledger(
    ledger_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi import HTTPException, status
    result = await db.execute(select(Ledger).where(Ledger.id == ledger_id, Ledger.company_id == company.id))
    ledger = result.scalar_one_or_none()
    if not ledger:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ledger not found")
    await db.delete(ledger)
    await db.flush()


@router.get("/{company_id}/ledgers/search", response_model=list[LedgerResponse])
async def search_ledgers(
    q: str = Query(..., min_length=1),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    pattern = f"%{q}%"
    result = await db.execute(
        select(Ledger).where(
            Ledger.company_id == company.id,
            or_(Ledger.name.ilike(pattern), (Ledger.alias or "").ilike(pattern)),
        ).order_by(Ledger.name).limit(50)
    )
    return [LedgerResponse.model_validate(l) for l in result.scalars().all()]
