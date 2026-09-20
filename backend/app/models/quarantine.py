from sqlalchemy import Column, Integer, String, Text, DateTime, func, JSON
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class QuarantineItem(Base):
    __tablename__ = "quarantine_items"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    sync_direction = Column(String(50), nullable=False, default="MIS_TO_UNTIS")
    lesson_id = Column(String(100), nullable=True, index=True)
    entity_type = Column(String(50), nullable=True)
    error_type = Column(String(50), nullable=True)
    details = Column(Text, nullable=True)
    raw_payload = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")
    resolved_override = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<QuarantineItem(id={self.id}, error_type='{self.error_type}', status='{self.status}')>"