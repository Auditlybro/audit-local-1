"""Stock items CRUD, summary, movement."""
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_current_user, get_company_for_user
from db.database import get_db
from models import Company, StockItem, StockGroup, InvoiceItem, Voucher
from schemas.stock import StockItemCreate, StockItemUpdate, StockItemResponse, StockSummaryItem, StockMovementItem

router = APIRouter(tags=["stock"])


@router.get("/{company_id}/stock-items", response_model=list[StockItemResponse])
async def list_stock_items(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StockItem).where(StockItem.company_id == company.id).order_by(StockItem.name))
    return [StockItemResponse.model_validate(i) for i in result.scalars().all()]


@router.post("/{company_id}/stock-items", response_model=StockItemResponse, status_code=201)
async def create_stock_item(
    body: StockItemCreate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    item = StockItem(
        company_id=company.id,
        group_id=body.group_id,
        name=body.name,
        hsn_code=body.hsn_code,
        sac_code=body.sac_code,
        unit=body.unit,
        gst_rate=body.gst_rate,
        mrp=body.mrp,
        opening_qty=body.opening_qty,
        opening_value=body.opening_value,
        reorder_level=body.reorder_level,
        batch_tracking=body.batch_tracking,
        expiry_tracking=body.expiry_tracking,
    )
    db.add(item)
    await db.flush()
    return StockItemResponse.model_validate(item)


@router.put("/{company_id}/stock-items/{item_id}", response_model=StockItemResponse)
async def update_stock_item(
    item_id: UUID,
    body: StockItemUpdate,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StockItem).where(StockItem.id == item_id, StockItem.company_id == company.id))
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock item not found")
    if body.group_id is not None:
        item.group_id = body.group_id
    if body.name is not None:
        item.name = body.name
    if body.hsn_code is not None:
        item.hsn_code = body.hsn_code
    if body.sac_code is not None:
        item.sac_code = body.sac_code
    if body.unit is not None:
        item.unit = body.unit
    if body.gst_rate is not None:
        item.gst_rate = body.gst_rate
    if body.mrp is not None:
        item.mrp = body.mrp
    if body.reorder_level is not None:
        item.reorder_level = body.reorder_level
    if body.batch_tracking is not None:
        item.batch_tracking = body.batch_tracking
    if body.expiry_tracking is not None:
        item.expiry_tracking = body.expiry_tracking
    await db.flush()
    return StockItemResponse.model_validate(item)


@router.get("/{company_id}/stock-summary", response_model=list[StockSummaryItem])
async def stock_summary(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StockItem).where(StockItem.company_id == company.id))
    items = result.scalars().all()
    out = []
    for i in items:
        qty = i.opening_qty or Decimal("0")
        val = i.opening_value or Decimal("0")
        out.append(StockSummaryItem(item_id=i.id, name=i.name, quantity=qty, value=val, unit=i.unit))
    return out


@router.get("/{company_id}/stock-items/{item_id}/movement", response_model=list[StockMovementItem])
async def stock_movement(
    item_id: UUID,
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(StockItem).where(StockItem.id == item_id, StockItem.company_id == company.id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stock item not found")
    # Get invoice items for this stock item
    result2 = await db.execute(
        select(InvoiceItem, Voucher).join(Voucher, InvoiceItem.voucher_id == Voucher.id).where(
            InvoiceItem.stock_item_id == item_id,
            Voucher.company_id == company.id,
            Voucher.is_cancelled == False,
        ).order_by(Voucher.date)
    )
    rows = result2.all()
    out = []
    balance = Decimal("0")
    for inv, v in rows:
        in_qty = inv.quantity if v.voucher_type in ("PURCHASE", "RECEIPT_NOTE", "STOCK_JOURNAL") else Decimal("0")
        out_qty = inv.quantity if v.voucher_type in ("SALES", "DELIVERY_NOTE", "STOCK_JOURNAL") else Decimal("0")
        balance += in_qty - out_qty
        out.append(StockMovementItem(
            date=v.date.isoformat(),
            voucher_type=v.voucher_type,
            voucher_id=v.id,
            in_qty=in_qty,
            out_qty=out_qty,
            balance=balance,
        ))
    return out
