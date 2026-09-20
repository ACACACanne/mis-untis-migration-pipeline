from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, func
from app.core.database import Base

class KeyRegistry(Base):
    __tablename__ = "key_registry"
    __table_args__ = {"extend_existing": True}  # Allow table to be extended if it already exists

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False, index=True)  # teacher, room, subject, class, student
    untis_id = Column(String(100), nullable=False, index=True)
    arbor_id = Column(String(100), nullable=True, index=True)
    bromcom_id = Column(String(100), nullable=True, index=True)
    short_code = Column(String(50), nullable=True)
    display_name = Column(String(255), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint('entity_type', 'untis_id', name='uq_entity_untis_id'),
    )

    def __repr__(self):
        return (
            f"<KeyRegistry(entity_type={self.entity_type}, "
            f"untis_id={self.untis_id}, "
            f"arbor_id={self.arbor_id}, "
            f"bromcom_id={self.bromcom_id})>"
        )