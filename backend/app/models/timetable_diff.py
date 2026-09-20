from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base


class TimetableDiff(Base):
    __tablename__ = "timetable_diff"
    __table_args__ = {"extend_existing": True}  # Allow table to be extended if it already exists

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_mis = Column(String(20), nullable=False, index=True)  # ARBOR or BROMCOM
    untis_lesson_id = Column(String(100), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    period_number = Column(Integer, nullable=False)
    # Change type classification: CREATE, UPDATE, DELETE, UNCHANGED
    change_type = Column(String(30), nullable=False, index=True)
    staged_slot_payload = Column(JSONB, nullable=False)
    # Status lifecycle: STAGED, COMMITTED, FAILED
    status = Column(String(30), nullable=False, server_default="STAGED", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<TimetableDiff(lesson='{self.untis_lesson_id}', day={self.day_number}, period={self.period_number}, change='{self.change_type}')>"