"""Ledger schemas."""
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class BalanceItem(BaseModel):
    from_user_id: UUID
    to_user_id: UUID
    amount: Decimal
    updated_at: datetime

    class Config:
        from_attributes = True


class LedgerBalancesResponse(BaseModel):
    group_id: UUID
    balances: list[BalanceItem]
