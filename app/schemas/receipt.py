"""Receipt schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, HttpUrl


class ReceiptCreate(BaseModel):
    image_url: str  # HttpUrl restricts to valid URLs; use str for flexibility


class ReceiptResponse(BaseModel):
    id: UUID
    expense_id: UUID
    image_url: str
    uploaded_by: UUID
    uploaded_at: datetime

    class Config:
        from_attributes = True
