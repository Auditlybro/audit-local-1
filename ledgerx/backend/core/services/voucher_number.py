"""Voucher number generation: TYPE/FY/NNNN."""
import re
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Voucher
from utils.indian_format import financial_year


async def next_voucher_number(
    db: AsyncSession,
    company_id,
    voucher_type: str,
    date,
) -> str:
    """Generate next number for type: e.g. SALES/2025-26/0001."""
    fy = financial_year(date)
    prefix = f"{voucher_type}/{fy}/"
    result = await db.execute(
        select(Voucher.number).where(
            Voucher.company_id == company_id,
            Voucher.voucher_type == voucher_type,
            Voucher.number.like(f"{prefix}%"),
        ).order_by(Voucher.number.desc()).limit(1)
    )
    row = result.scalar_one_or_none()
    last = 0
    if row:
        match = re.search(r"/(\d+)$", row)
        if match:
            last = int(match.group(1))
    return f"{prefix}{(last + 1):04d}"
