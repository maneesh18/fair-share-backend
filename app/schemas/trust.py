"""Trust schemas."""
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel


class TrustScoreItem(BaseModel):
    user_id: UUID
    name: str | None
    trust_score: Decimal
    rank: int | None = None

    class Config:
        from_attributes = True


class TrustScoresResponse(BaseModel):
    group_id: UUID
    scores: list[TrustScoreItem]
