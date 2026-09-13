from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.core.database import Base


class SyncAudit(Base):
    __tablename__ = "sync_audit"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sync_direction = Column(String(20), nullable=False, index=True)  # UNTIS_TO_MIS or MIS_TO_UNTIS
    status = Column(String(30), nullable=False, index=True)  # RUNNING, COMPLETED, FAILED
    total_records = Column(Integer, default=0)
    staged_records = Column(Integer, default=0)
    quarantined_records = Column(Integer, default=0)
    committed_records = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<SyncAudit(id={self.id}, direction='{self.sync_direction}', status='{self.status}')>"