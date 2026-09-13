from typing import Any, Dict, Optional, cast
from sqlalchemy.orm import Session
from app.models.quarantine import QuarantineItem


class QuarantineResolver:
    """Applies administrative overrides to quarantined timetable items."""

    def __init__(self, db: Session):
        self.db = db

    def resolve_item(
        self, item_id: int, status: str, override_data: Dict[str, Any]
    ) -> Optional[QuarantineItem]:
        """
        Updates the quarantine item status to RESOLVED or IGNORED and records override details.
        """
        item = self.db.query(QuarantineItem).filter(QuarantineItem.id == item_id).first()
        if not item:
            return None

        # Use setattr or cast to satisfy static type checkers on SQLAlchemy column assignments
        target = cast(Any, item)
        target.status = status.upper()
        target.resolved_override = override_data

        self.db.commit()
        self.db.refresh(item)
        return item

    def apply_override_to_slot(
        self, original_slot: Dict[str, Any], override_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merges administrative override fields into the slot payload."""
        updated_slot = dict(original_slot)

        if "override_teacher_id" in override_data:
            updated_slot["teacher_id"] = override_data["override_teacher_id"]
            updated_slot["mis_staff_id"] = override_data.get("override_mis_staff_id")

        if "override_room_code" in override_data:
            updated_slot["room_code"] = override_data["override_room_code"]
            updated_slot["mis_room_id"] = override_data.get("override_mis_room_id")

        return updated_slot