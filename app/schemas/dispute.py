"""Dispute schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class DisputeCreate(BaseModel):
    reason: str


class DisputeResponse(BaseModel):
    id: UUID
    expense_id: UUID
    raised_by: UUID
    reason: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
