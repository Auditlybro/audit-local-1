"""Banking: accounts, import statement, reconcile, BRS."""
from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.dependencies import get_company_for_user
from db.database import get_db
from models import Company, BankAccount, BankTransaction, Ledger
from schemas.banking import BankAccountResponse, BankTransactionRow, ReconcileMatchRequest, BRSResponse

router = APIRouter(tags=["banking"])


@router.get("/{company_id}/banking/accounts", response_model=list[BankAccountResponse])
async def list_bank_accounts(
    company: Company = Depends(get_company_for_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).join(Ledger, BankAccount.ledger_id == Ledger.id).where(Ledger.company_id == company.id)
    )
    return [BankAccountResponse.model_validate(a) for a in result.scalars().all()]


@router.post("/{company_id}/banking/accounts/{acc_id}/import-statement")
async def import_statement(
  acc_id: UUID,
  file: UploadFile = File(...),
  company: Company = Depends(get_company_for_user),
  db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).join(Ledger, BankAccount.ledger_id == Ledger.id).where(
            BankAccount.id == acc_id,
            Ledger.company_id == company.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bank account not found")
    content = await file.read()
    # Placeholder: parse CSV/Excel and create BankTransaction rows
    return {"status": "ok", "imported": 0, "message": "Upload received; parsing not implemented"}


@router.get("/{company_id}/banking/accounts/{acc_id}/reconcile")
async def get_reconcile(
  acc_id: UUID,
  company: Company = Depends(get_company_for_user),
  db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).join(Ledger, BankAccount.ledger_id == Ledger.id).where(
            BankAccount.id == acc_id,
            Ledger.company_id == company.id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Bank account not found")
    result2 = await db.execute(select(BankTransaction).where(BankTransaction.bank_account_id == acc_id).order_by(BankTransaction.transaction_date))
    txns = [BankTransactionRow(id=t.id, transaction_date=t.transaction_date.isoformat(), description=t.description, debit=t.debit, credit=t.credit, balance=t.balance, reconciled=t.reconciled, voucher_id=t.voucher_id) for t in result2.scalars().all()]
    return {"bank_account_id": str(acc_id), "transactions": txns}


@router.post("/{company_id}/banking/accounts/{acc_id}/reconcile/match")
async def reconcile_match(
  acc_id: UUID,
  body: ReconcileMatchRequest,
  company: Company = Depends(get_company_for_user),
  db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankTransaction).join(BankAccount, BankTransaction.bank_account_id == BankAccount.id).join(
            Ledger, BankAccount.ledger_id == Ledger.id
        ).where(
            BankTransaction.id == body.bank_transaction_id,
            BankTransaction.bank_account_id == acc_id,
            Ledger.company_id == company.id,
        )
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    t.voucher_id = body.voucher_id
    t.reconciled = True
    await db.flush()
    return {"status": "ok"}


@router.get("/{company_id}/banking/accounts/{acc_id}/brs", response_model=BRSResponse)
async def get_brs(
  acc_id: UUID,
  as_on: str = None,
  company: Company = Depends(get_company_for_user),
  db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BankAccount).join(Ledger, BankAccount.ledger_id == Ledger.id).where(
            BankAccount.id == acc_id,
            Ledger.company_id == company.id,
        )
    )
    acc = result.scalar_one_or_none()
    if not acc:
        raise HTTPException(status_code=404, detail="Bank account not found")
    return BRSResponse(
        bank_account_id=acc.id,
        as_on_date=as_on or "",
        bank_balance=acc.opening_balance or 0,
        book_balance=acc.opening_balance or 0,
        unmatched_bank=[],
        unmatched_book=[],
    )
