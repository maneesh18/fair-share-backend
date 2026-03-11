"""Analytics schemas."""
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class AnalyticsResponse(BaseModel):
    group_id: UUID
    period: str
    total_spend: float
    spend_by_user: dict[str, float]
    spend_by_category: dict[str, float]
    highest_trust_user: str | None
    lowest_trust_user: str | None
    most_disputed_user: str | None
    computed_at: datetime
