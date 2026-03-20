"""Banking schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class BankAccountResponse(BaseModel):
    id: UUID
    ledger_id: UUID
    account_number: str
    ifsc: str | None
    bank_name: str | None
    branch: str | None
    opening_balance: Decimal
    reconciled_till: str | None

    class Config:
        from_attributes = True


class BankTransactionRow(BaseModel):
    id: UUID
    transaction_date: str
    description: str | None
    debit: Decimal
    credit: Decimal
    balance: Decimal | None
    reconciled: bool
    voucher_id: UUID | None


class ReconcileMatchRequest(BaseModel):
    bank_transaction_id: UUID
    voucher_id: UUID


class BRSResponse(BaseModel):
    bank_account_id: UUID
    as_on_date: str
    bank_balance: Decimal
    book_balance: Decimal
    unmatched_bank: list[dict]
    unmatched_book: list[dict]
