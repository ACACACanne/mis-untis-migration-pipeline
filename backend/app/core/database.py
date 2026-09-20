from typing import Generator
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.core.config import settings

# SQLite requires check_same_thread=False for multithreaded applications like FastAPI
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class TimetableDiff(Base):
    __tablename__ = "timetable_diff"

    id = Column(Integer, primary_key=True, autoincrement=True)
    target_mis = Column(String(20), nullable=False, index=True)
    untis_lesson_id = Column(String(100), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)
    period_number = Column(Integer, nullable=False)
    change_type = Column(String(30), nullable=False, index=True)
    staged_slot_payload = Column(JSONB, nullable=False)
    status = Column(String(30), nullable=False, server_default="STAGED", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return (
            f"<TimetableDiff(lesson='{self.untis_lesson_id}', "
            f"day={self.day_number}, period={self.period_number}, "
            f"change='{self.change_type}')>"
        )


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding isolated database sessions per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()