"""Report response schemas."""
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel


class TrialBalanceRow(BaseModel):
    ledger_id: UUID
    ledger_name: str
    group_name: str
    debit: Decimal
    credit: Decimal


class TrialBalanceResponse(BaseModel):
    from_date: str
    to_date: str
    rows: list[TrialBalanceRow]
    total_debit: Decimal
    total_credit: Decimal


class BalanceSheetSection(BaseModel):
    name: str
    items: list[dict]
    total: Decimal


class BalanceSheetResponse(BaseModel):
    date: str
    assets: list[BalanceSheetSection]
    liabilities: list[BalanceSheetSection]


class ProfitLossResponse(BaseModel):
    from_date: str
    to_date: str
    revenue: Decimal
    expenses: Decimal
    net_profit: Decimal
    sections: list[dict]


class LedgerReportRow(BaseModel):
    date: str
    voucher_type: str
    number: str | None
    narration: str | None
    debit: Decimal
    credit: Decimal
    balance: Decimal


class LedgerReportResponse(BaseModel):
    ledger_id: UUID
    ledger_name: str
    from_date: str
    to_date: str
    opening_balance: Decimal
    rows: list[LedgerReportRow]
    closing_balance: Decimal


class OutstandingItem(BaseModel):
    ledger_id: UUID
    name: str
    amount: Decimal
    due_days: int | None


class CashFlowSection(BaseModel):
    name: str
    amount: Decimal
    items: list[dict]


class SalesRegisterRow(BaseModel):
    date: str
    number: str | None
    party: str
    taxable_value: Decimal
    gst: Decimal
    total: Decimal


class StockAgeingRow(BaseModel):
    item_id: UUID
    item_name: str
    quantity: Decimal
    value: Decimal
    age_days: int
    bucket: str
