"""Inventory: stock movement, value (FIFO/LIFO/AvgCost), availability check."""
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import StockItem, InvoiceItem, Voucher


async def update_stock(
    db: AsyncSession,
    item_id: UUID,
    qty: Decimal,
    rate: Decimal,
    godown_id: UUID | None,
    movement_type: str,
) -> None:
    """
    movement_type: 'in' or 'out'.
    Updates stock item's opening_qty and opening_value (simplified; full impl would use stock_ledger).
    """
    result = await db.execute(select(StockItem).where(StockItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return
    if movement_type == "in":
        item.opening_qty = (item.opening_qty or 0) + qty
        item.opening_value = (item.opening_value or 0) + (qty * rate)
    else:
        old_qty = item.opening_qty or 0
        item.opening_qty = old_qty - qty
        if old_qty and old_qty != 0:
            item.opening_value = (item.opening_value or 0) * (item.opening_qty / old_qty)
        else:
            item.opening_value = Decimal("0")
    await db.flush()


async def get_stock_value(
    db: AsyncSession,
    item_id: UUID,
    method: str = "AvgCost",
) -> Decimal:
    """FIFO/LIFO/AvgCost. Simplified: return opening_value for AvgCost."""
    result = await db.execute(select(StockItem).where(StockItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item or not item.opening_qty:
        return Decimal("0")
    if method == "AvgCost" or method == "avg":
        return (item.opening_value or 0) / (item.opening_qty or 1)
    # FIFO/LIFO would need stock_ledger table
    return (item.opening_value or 0) / (item.opening_qty or 1)


async def check_stock_availability(db: AsyncSession, item_id: UUID, qty: Decimal) -> bool:
    result = await db.execute(select(StockItem).where(StockItem.id == item_id))
    item = result.scalar_one_or_none()
    if not item:
        return False
    return (item.opening_qty or 0) >= qty
