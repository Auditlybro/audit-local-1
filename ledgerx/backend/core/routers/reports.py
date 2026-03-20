"""Reports: trial balance, balance sheet, P&L, ledger, outstanding, cash flow, registers."""
from decimal import Decimal
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_company_for_user
from db.database import get_db
from models import Company, Ledger, LedgerGroup, Voucher, VoucherEntry

router = APIRouter(tags=["reports"])


@router.get("/{company_id}/reports/trial-balance")
async def trial_balance(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    # Sum of dr/cr per ledger in period + opening
    result = await db.execute(
        select(Ledger.id, Ledger.name, LedgerGroup.name.label("group_name"), Ledger.opening_balance).join(
            LedgerGroup, Ledger.group_id == LedgerGroup.id
        ).where(Ledger.company_id == company.id)
    )
    ledgers = result.all()
    rows = []
    total_dr = total_cr = Decimal("0")
    for l_id, lname, gname, open_bal in ledgers:
        # Opening: Assets/Expense = debit nature, Liability/Income = credit
        result2 = await db.execute(
            select(func.coalesce(func.sum(VoucherEntry.dr_amount), 0), func.coalesce(func.sum(VoucherEntry.cr_amount), 0)).select_from(
                VoucherEntry
            ).join(Voucher, VoucherEntry.voucher_id == Voucher.id).where(
                Voucher.company_id == company.id,
                Voucher.date >= from_date,
                Voucher.date <= to_date,
                Voucher.is_cancelled == False,
                VoucherEntry.ledger_id == l_id,
            )
        )
        dr, cr = result2.one()
        dr = (dr or 0) + (open_bal if open_bal and open_bal > 0 else 0)
        cr = (cr or 0) + (-open_bal if open_bal and open_bal < 0 else 0)
        if dr != cr:
            rows.append({"ledger_id": l_id, "ledger_name": lname, "group_name": gname, "debit": dr, "credit": cr})
            total_dr += dr
            total_cr += cr
    return {"from_date": str(from_date), "to_date": str(to_date), "rows": rows, "total_debit": total_dr, "total_credit": total_cr}


@router.get("/{company_id}/reports/balance-sheet")
async def balance_sheet(
    as_on: date = Query(..., alias="date"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ledger.id, Ledger.name, LedgerGroup.name, LedgerGroup.nature, Ledger.opening_balance).join(
            LedgerGroup, Ledger.group_id == LedgerGroup.id
        ).where(Ledger.company_id == company.id)
    )
    items = result.all()
    assets = [{"name": r[1], "amount": r[4] or 0} for r in items if r[3] == "Assets"]
    liabilities = [{"name": r[1], "amount": r[4] or 0} for r in items if r[3] == "Liabilities"]
    return {"date": str(as_on), "assets": assets, "liabilities": liabilities}


@router.get("/{company_id}/reports/profit-loss")
async def profit_loss(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(LedgerGroup.nature, func.sum(Ledger.opening_balance)).join(
            Ledger, Ledger.group_id == LedgerGroup.id
        ).where(Ledger.company_id == company.id).group_by(LedgerGroup.nature)
    )
    rev = exp = Decimal("0")
    for nature, bal in result.all():
        if nature == "Income":
            rev += bal or 0
        elif nature == "Expense":
            exp += bal or 0
    return {"from_date": str(from_date), "to_date": str(to_date), "revenue": rev, "expenses": exp, "net_profit": rev - exp, "sections": []}


@router.get("/{company_id}/reports/ledger/{ledger_id}")
async def ledger_report(
    ledger_id: UUID,
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Ledger).where(Ledger.id == ledger_id, Ledger.company_id == company.id))
    ledger = result.scalar_one_or_none()
    if not ledger:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=404, detail="Ledger not found")
    result2 = await db.execute(
        select(Voucher.date, Voucher.voucher_type, Voucher.number, Voucher.narration, VoucherEntry.dr_amount, VoucherEntry.cr_amount).join(
            VoucherEntry, Voucher.id == VoucherEntry.voucher_id
        ).where(
            Voucher.company_id == company.id,
            VoucherEntry.ledger_id == ledger_id,
            Voucher.date >= from_date,
            Voucher.date <= to_date,
            Voucher.is_cancelled == False,
        ).order_by(Voucher.date)
    )
    rows = []
    balance = ledger.opening_balance or Decimal("0")
    for d, vtype, num, narr, dr, cr in result2.all():
        balance = balance + (dr or 0) - (cr or 0)
        rows.append({"date": str(d), "voucher_type": vtype, "number": num, "narration": narr, "debit": dr or 0, "credit": cr or 0, "balance": balance})
    return {"ledger_id": ledger_id, "ledger_name": ledger.name, "from_date": str(from_date), "to_date": str(to_date), "opening_balance": ledger.opening_balance or 0, "rows": rows, "closing_balance": balance}


@router.get("/{company_id}/reports/outstanding/receivables")
async def outstanding_receivables(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    # Sundry Debtors: sum of ledger balances (simplified)
    result = await db.execute(
        select(Ledger.id, Ledger.name).join(LedgerGroup, Ledger.group_id == LedgerGroup.id).where(
            Ledger.company_id == company.id,
            LedgerGroup.name == "Sundry Debtors",
        )
    )
    items = [{"ledger_id": r[0], "name": r[1], "amount": 0} for r in result.all()]
    return {"items": items}


@router.get("/{company_id}/reports/outstanding/payables")
async def outstanding_payables(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Ledger.id, Ledger.name).join(LedgerGroup, Ledger.group_id == LedgerGroup.id).where(
            Ledger.company_id == company.id,
            LedgerGroup.name == "Sundry Creditors",
        )
    )
    items = [{"ledger_id": r[0], "name": r[1], "amount": 0} for r in result.all()]
    return {"items": items}


@router.get("/{company_id}/reports/cash-flow")
async def cash_flow(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    return {"from_date": str(from_date), "to_date": str(to_date), "sections": []}


@router.get("/{company_id}/reports/sales-register")
async def sales_register(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    from models import InvoiceItem
    result = await db.execute(
        select(Voucher.date, Voucher.number, Voucher.party_ledger_id, InvoiceItem.taxable_value, InvoiceItem.cgst_amount + InvoiceItem.sgst_amount + InvoiceItem.igst_amount, InvoiceItem.total_amount).join(
            InvoiceItem, Voucher.id == InvoiceItem.voucher_id
        ).where(
            Voucher.company_id == company.id,
            Voucher.voucher_type == "SALES",
            Voucher.date >= from_date,
            Voucher.date <= to_date,
            Voucher.is_cancelled == False,
        ).order_by(Voucher.date)
    )
    rows = [{"date": str(r[0]), "number": r[1], "party": str(r[2]), "taxable_value": r[3], "gst": r[4], "total": r[5]} for r in result.all()]
    return {"from_date": str(from_date), "to_date": str(to_date), "rows": rows}


@router.get("/{company_id}/reports/purchase-register")
async def purchase_register(
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    from models import InvoiceItem
    result = await db.execute(
        select(Voucher.date, Voucher.number, InvoiceItem.taxable_value, InvoiceItem.total_amount).join(
            InvoiceItem, Voucher.id == InvoiceItem.voucher_id
        ).where(
            Voucher.company_id == company.id,
            Voucher.voucher_type == "PURCHASE",
            Voucher.date >= from_date,
            Voucher.date <= to_date,
            Voucher.is_cancelled == False,
        ).order_by(Voucher.date)
    )
    rows = [{"date": str(r[0]), "number": r[1], "taxable_value": r[2], "total": r[3]} for r in result.all()]
    return {"from_date": str(from_date), "to_date": str(to_date), "rows": rows}


@router.get("/{company_id}/reports/stock-ageing")
async def stock_ageing(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    from models import StockItem
    result = await db.execute(select(StockItem).where(StockItem.company_id == company.id))
    items = result.scalars().all()
    rows = [{"item_id": i.id, "item_name": i.name, "quantity": i.opening_qty or 0, "value": i.opening_value or 0, "age_days": 0, "bucket": "current"} for i in items]
    return {"rows": rows}
