"""Expense schemas."""
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel, Field


class ExpenseSplitCreate(BaseModel):
    user_id: UUID
    amount: Decimal = Field(gt=0)


class ExpenseCreate(BaseModel):
    group_id: UUID
    total_amount: Decimal = Field(gt=0)
    currency: str = "USD"
    category: str
    description: str | None = None
    splits: list[ExpenseSplitCreate]


class ExpenseUpdate(BaseModel):
    total_amount: Decimal | None = Field(None, gt=0)
    category: str | None = None
    description: str | None = None
    splits: list[ExpenseSplitCreate] | None = None


class ExpenseSplitResponse(BaseModel):
    id: UUID
    user_id: UUID
    amount: Decimal

    class Config:
        from_attributes = True


class ExpenseResponse(BaseModel):
    id: UUID
    group_id: UUID
    created_by: UUID
    total_amount: Decimal
    currency: str
    category: str
    description: str | None
    status: str
    created_at: datetime
    splits: list[ExpenseSplitResponse] = []

    class Config:
        from_attributes = True
