from sqlalchemy import Column, Integer, String, Text, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class QuarantineItem(Base):
    __tablename__ = "quarantine_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_direction = Column(String(20), nullable=False, default="UNTIS_TO_MIS")
    lesson_id = Column(String(100), nullable=True, index=True)
    entity_type = Column(String(50), nullable=False)
    # Error classification: COLLISION, UNASSIGNED_ROOM, UNMAPPED_STUDENT, DUTY_PERIOD
    error_type = Column(String(100), nullable=False, index=True)
    details = Column(Text, nullable=False)
    raw_payload = Column(JSONB, nullable=False)
    # Status lifecycle: PENDING, RESOLVED, IGNORED
    status = Column(String(30), nullable=False, server_default="PENDING", index=True)
    resolved_override = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<QuarantineItem(id={self.id}, error_type='{self.error_type}', status='{self.status}')>"