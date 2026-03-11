"""Analytics router."""
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.modules.analytics.service import get_or_compute_analytics
from app.modules.groups.service import is_member
from app.modules.auth.dependencies import get_current_user

router = APIRouter(tags=["analytics"])


@router.get("/groups/{group_id}/analytics", response_model=AnalyticsResponse)
def get_analytics(
    group_id: UUID,
    period: str = Query("all", description="Period: 'all' or e.g. '2025-03'"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not is_member(db, group_id, user.id):
        raise HTTPException(status_code=403, detail="Not a member of this group")
    metrics = get_or_compute_analytics(db, group_id, period)
    return AnalyticsResponse(
        group_id=group_id,
        period=period,
        total_spend=metrics.get("total_spend", 0),
        spend_by_user=metrics.get("spend_by_user", {}),
        spend_by_category=metrics.get("spend_by_category", {}),
        highest_trust_user=metrics.get("highest_trust_user"),
        lowest_trust_user=metrics.get("lowest_trust_user"),
        most_disputed_user=metrics.get("most_disputed_user"),
        computed_at=datetime.utcnow(),
    )
