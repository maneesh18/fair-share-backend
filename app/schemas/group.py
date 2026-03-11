"""Group schemas."""
from datetime import datetime
from uuid import UUID
from decimal import Decimal
from pydantic import BaseModel


class GroupCreate(BaseModel):
    name: str


class GroupResponse(BaseModel):
    id: UUID
    name: str
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class GroupMemberAdd(BaseModel):
    user_id: UUID


class GroupMemberResponse(BaseModel):
    id: UUID
    group_id: UUID
    user_id: UUID
    role: str
    trust_score: Decimal
    joined_at: datetime

    class Config:
        from_attributes = True


class GroupMemberWithUser(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    trust_score: Decimal
    joined_at: datetime
    name: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True
