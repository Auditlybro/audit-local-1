"""GST calculation: CGST/SGST (intrastate), IGST (interstate)."""
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Ledger, Company


def calculate_gst(
    amount: Decimal,
    rate: Decimal,
    supply_type: str = "intrastate",
) -> dict[str, Decimal]:
    """
    supply_type: 'intrastate' -> CGST + SGST (half each); 'interstate' -> IGST.
    Returns {cgst, sgst, igst} in rupees.
    """
    tax = (amount * rate / 100).quantize(Decimal("0.01"))
    half = (tax / 2).quantize(Decimal("0.01"))
    if supply_type == "interstate":
        return {"cgst": Decimal("0"), "sgst": Decimal("0"), "igst": tax}
    return {"cgst": half, "sgst": half, "igst": Decimal("0")}


def is_interstate(from_state: str, to_state: str) -> bool:
    """Same state code = intrastate."""
    if not from_state or not to_state:
        return True
    return from_state.strip().upper() != to_state.strip().upper()


async def get_tax_ledgers(
    db: AsyncSession,
    company_id: UUID,
    rate: Decimal,
    nature: str = "Liabilities",
) -> list[UUID]:
    """
    Return ledger IDs for Duties & Taxes (GST) for given rate.
    Typically one ledger per rate under "Duties & Taxes" group.
    """
    from models import LedgerGroup
    result = await db.execute(
        select(Ledger.id).join(LedgerGroup, Ledger.group_id == LedgerGroup.id).where(
            Ledger.company_id == company_id,
            LedgerGroup.name == "Duties & Taxes",
            LedgerGroup.company_id == company_id,
        )
    )
    return [r[0] for r in result.all()]
