# backend/app/models/timetable_diff.py

from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class TimetableDiff(Base):
    __tablename__ = "timetable_diff"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    target_mis = Column(String(50), nullable=False, default="ARBOR")
    untis_lesson_id = Column(String(100), nullable=True, index=True)
    day_number = Column(Integer, nullable=True)
    period_number = Column(Integer, nullable=True)
    change_type = Column(String(20), nullable=False, index=True)  # Single index definition
    slot_payload = Column(JSON, nullable=True)
    staged_slot_payload = Column(JSON, nullable=True)
    status = Column(String(20), nullable=False, default="STAGED", index=True)  # Single index definition
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TimetableDiff(lesson='{self.untis_lesson_id}', day={self.day_number}, period={self.period_number}, change='{self.change_type}')>"