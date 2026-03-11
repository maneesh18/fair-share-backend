"""AnalyticsSnapshot model."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db import Base


class AnalyticsSnapshot(Base):
    __tablename__ = "analytics_snapshots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), nullable=False)
    period = Column(String(50), nullable=False)  # e.g. "2025-03", "all"
    metrics_json = Column(JSONB, nullable=False)
    computed_at = Column(DateTime, default=datetime.utcnow)
