"""Double-entry validation and posting."""
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Voucher, VoucherEntry, Ledger


def validate_entry(entries: list[dict]) -> bool:
    """
    Validate that total Dr = total Cr (double-entry).
    Each entry has dr_amount, cr_amount (Decimal or int in paise).
    """
    total_dr = sum(Decimal(str(e.get("dr_amount", 0))) for e in entries)
    total_cr = sum(Decimal(str(e.get("cr_amount", 0))) for e in entries)
    return total_dr == total_cr and (total_dr > 0 or total_cr > 0)


async def post_voucher(db: AsyncSession, voucher: Voucher) -> None:
    """
    Update ledger running balances for all entries of this voucher.
    Assumes ledger has opening_balance; we don't have a separate running_balance column
    in schema - so we only validate. For full running balance we'd need a balance column
    or compute from voucher_entries. Schema has opening_balance on ledgers only.
    So: post_voucher = persist voucher + entries; no balance column to update unless we add one.
    """
    # Persist is done by router. Here we can recompute and update ledger balances if we add
    # a current_balance column. For now, just ensure voucher is committed (caller commits).
    for entry in voucher.entries:
        # Optional: update ledger's running balance if we add that column
        pass
    await db.flush()


async def reverse_voucher(db: AsyncSession, voucher_id: str, company_id: str) -> Voucher | None:
    """
    Create a reversing journal voucher with opposite Dr/Cr for each entry.
    Returns the new reversal voucher.
    """
    from uuid import UUID
    from datetime import date
    result = await db.execute(
        select(Voucher).where(
            Voucher.id == UUID(voucher_id),
            Voucher.company_id == UUID(company_id),
            Voucher.is_cancelled == False,
        )
    )
    orig = result.scalar_one_or_none()
    if not orig:
        return None
    rev = Voucher(
        company_id=orig.company_id,
        voucher_type="REVERSING_JOURNAL",
        date=date.today(),
        narration=f"Reversal of {orig.voucher_type} #{orig.number or orig.id}",
        source="api",
    )
    db.add(rev)
    await db.flush()
    for e in orig.entries:
        rev_entry = VoucherEntry(
            voucher_id=rev.id,
            ledger_id=e.ledger_id,
            dr_amount=e.cr_amount,
            cr_amount=e.dr_amount,
            narration=e.narration,
        )
        db.add(rev_entry)
    orig.is_cancelled = True
    return rev
