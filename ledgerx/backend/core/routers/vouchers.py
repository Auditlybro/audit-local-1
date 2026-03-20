"""Vouchers CRUD, cancel, day-book."""
from decimal import Decimal
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, get_company_for_user
from db.database import get_db
from models import User, Company, Voucher, VoucherEntry, Ledger, InvoiceItem, StockItem
from schemas.voucher import VoucherCreate, VoucherUpdate, VoucherResponse, VoucherEntryResponse, VOUCHER_TYPES
from services.double_entry import validate_entry
from services.voucher_number import next_voucher_number
from services.inventory import update_stock, check_stock_availability

router = APIRouter(tags=["vouchers"])


def _entries_to_dict(entries: list) -> list[dict]:
    return [{"ledger_id": e.ledger_id, "dr_amount": e.dr_amount, "cr_amount": e.cr_amount} for e in entries]


@router.get("/{company_id}/vouchers", response_model=list[VoucherResponse])
async def list_vouchers(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
    from_date: date | None = Query(None, alias="from"),
    to_date: date | None = Query(None, alias="to"),
    voucher_type: str | None = None,
):
    q = select(Voucher).where(Voucher.company_id == company.id, Voucher.is_cancelled == False)
    if from_date:
        q = q.where(Voucher.date >= from_date)
    if to_date:
        q = q.where(Voucher.date <= to_date)
    if voucher_type:
        q = q.where(Voucher.voucher_type == voucher_type)
    q = q.order_by(Voucher.date.desc(), Voucher.created_at.desc())
    result = await db.execute(q)
    vouchers = result.scalars().all()
    return [_voucher_to_response(v) for v in vouchers]


@router.post("/{company_id}/vouchers", response_model=VoucherResponse, status_code=201)
async def create_voucher(
    body: VoucherCreate,
    current_user: User = Depends(get_current_user),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    if body.voucher_type not in VOUCHER_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid voucher_type. Allowed: {VOUCHER_TYPES}")
    entries_dict = [e.model_dump() for e in body.entries]
    if not validate_entry(entries_dict):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Debit total must equal Credit total")
    # Credit limit check for payment/receipt (party ledger)
    if body.voucher_type in ("PAYMENT", "RECEIPT") and body.party_ledger_id:
        result = await db.execute(select(Ledger).where(Ledger.id == body.party_ledger_id, Ledger.company_id == company.id))
        party = result.scalar_one_or_none()
        if party and party.credit_limit is not None:
            # Would need current outstanding; skip for now or sum from vouchers
            pass
    number = await next_voucher_number(db, company.id, body.voucher_type, body.date)
    voucher = Voucher(
        company_id=company.id,
        voucher_type=body.voucher_type,
        number=number,
        date=body.date,
        party_ledger_id=body.party_ledger_id,
        narration=body.narration,
        reference=body.reference,
        cost_centre=body.cost_centre,
        is_optional=body.is_optional,
        created_by=current_user.id,
        source="api",
    )
    voucher.amount = sum(Decimal(str(e.get("dr_amount", 0))) for e in entries_dict)
    db.add(voucher)
    await db.flush()
    for e in body.entries:
        ent = VoucherEntry(
            voucher_id=voucher.id,
            ledger_id=e.ledger_id,
            dr_amount=e.dr_amount,
            cr_amount=e.cr_amount,
            narration=e.narration,
            bill_ref=e.bill_ref,
            cost_centre=e.cost_centre,
        )
        db.add(ent)
    if body.invoice_items:
        for ii in body.invoice_items:
            if body.voucher_type in ("SALES", "DELIVERY_NOTE"):
                ok = await check_stock_availability(db, ii.stock_item_id, ii.quantity)
                if not ok:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for item {ii.stock_item_id}")
            inv = InvoiceItem(
                voucher_id=voucher.id,
                stock_item_id=ii.stock_item_id,
                godown_id=ii.godown_id,
                quantity=ii.quantity,
                rate=ii.rate,
                unit=ii.unit,
                discount_pct=ii.discount_pct,
                discount_amount=ii.discount_amount,
                taxable_value=ii.taxable_value,
                cgst_rate=ii.cgst_rate,
                cgst_amount=ii.cgst_amount,
                sgst_rate=ii.sgst_rate,
                sgst_amount=ii.sgst_amount,
                igst_rate=ii.igst_rate,
                igst_amount=ii.igst_amount,
                total_amount=ii.total_amount,
            )
            db.add(inv)
            await db.flush()
            if body.voucher_type in ("SALES", "DELIVERY_NOTE"):
                await update_stock(db, ii.stock_item_id, ii.quantity, ii.rate, ii.godown_id, "out")
            elif body.voucher_type in ("PURCHASE", "RECEIPT_NOTE"):
                await update_stock(db, ii.stock_item_id, ii.quantity, ii.rate, ii.godown_id, "in")
    await db.flush()
    await db.refresh(voucher)
    return _voucher_to_response(voucher)


def _voucher_to_response(v: Voucher) -> VoucherResponse:
    entries = [VoucherEntryResponse(id=e.id, ledger_id=e.ledger_id, dr_amount=e.dr_amount, cr_amount=e.cr_amount, narration=e.narration) for e in (v.entries or [])]
    return VoucherResponse(
        id=v.id,
        company_id=v.company_id,
        voucher_type=v.voucher_type,
        number=v.number,
        date=v.date,
        party_ledger_id=v.party_ledger_id,
        narration=v.narration,
        amount=v.amount,
        reference=v.reference,
        is_cancelled=v.is_cancelled,
        created_at=v.created_at.isoformat() if getattr(v, "created_at", None) else None,
        entries=entries,
    )


@router.get("/{company_id}/vouchers/{voucher_id}", response_model=VoucherResponse)
async def get_voucher(
    voucher_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Voucher).where(Voucher.id == voucher_id, Voucher.company_id == company.id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    await db.refresh(v)
    return _voucher_to_response(v)


@router.put("/{company_id}/vouchers/{voucher_id}", response_model=VoucherResponse)
async def update_voucher(
    voucher_id: UUID,
    body: VoucherUpdate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Voucher).where(Voucher.id == voucher_id, Voucher.company_id == company.id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    if v.is_cancelled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot edit cancelled voucher")
    if body.date is not None:
        v.date = body.date
    if body.party_ledger_id is not None:
        v.party_ledger_id = body.party_ledger_id
    if body.narration is not None:
        v.narration = body.narration
    if body.reference is not None:
        v.reference = body.reference
    if body.cost_centre is not None:
        v.cost_centre = body.cost_centre
    if body.entries is not None:
        if not validate_entry([e.model_dump() for e in body.entries]):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dr must equal Cr")
        for old in v.entries:
            await db.delete(old)
        await db.flush()
        for e in body.entries:
            ent = VoucherEntry(voucher_id=v.id, ledger_id=e.ledger_id, dr_amount=e.dr_amount, cr_amount=e.cr_amount, narration=e.narration, bill_ref=e.bill_ref, cost_centre=e.cost_centre)
            db.add(ent)
    await db.flush()
    await db.refresh(v)
    return _voucher_to_response(v)


@router.delete("/{company_id}/vouchers/{voucher_id}", status_code=204)
async def delete_voucher(
    voucher_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Voucher).where(Voucher.id == voucher_id, Voucher.company_id == company.id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    await db.delete(v)
    await db.flush()


@router.post("/{company_id}/vouchers/{voucher_id}/cancel", response_model=VoucherResponse)
async def cancel_voucher(
    voucher_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    from services.double_entry import reverse_voucher
    result = await db.execute(
        select(Voucher).where(Voucher.id == voucher_id, Voucher.company_id == company.id)
    )
    v = result.scalar_one_or_none()
    if not v:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Voucher not found")
    v.is_cancelled = True
    await db.flush()
    await db.refresh(v)
    return _voucher_to_response(v)


@router.get("/{company_id}/day-book")
async def day_book(
    date: date = Query(..., alias="date"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Voucher).where(
            Voucher.company_id == company.id,
            Voucher.date == date,
            Voucher.is_cancelled == False,
        ).order_by(Voucher.created_at)
    )
    vouchers = result.scalars().all()
    return {"date": date.isoformat(), "vouchers": [_voucher_to_response(v) for v in vouchers]}
