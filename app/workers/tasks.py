"""Celery tasks."""
from app.workers.celery_app import celery_app
from app.db import SessionLocal
from app.services.trust_engine import recalculate_trust_scores
from app.modules.analytics.service import compute_analytics
from uuid import UUID


@celery_app.task
def recalc_trust_score_task(group_id: str) -> None:
    """Recalculate trust scores for a group (runs in background)."""
    db = SessionLocal()
    try:
        recalculate_trust_scores(db, UUID(group_id))
    finally:
        db.close()


@celery_app.task
def compute_analytics_task(group_id: str, period: str = "all") -> None:
    """Compute and store analytics for a group (runs in background)."""
    db = SessionLocal()
    try:
        compute_analytics(db, UUID(group_id), period)
    finally:
        db.close()
