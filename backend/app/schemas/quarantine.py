from typing import Optional, Any, Dict
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class QuarantineItemBase(BaseModel):
    sync_direction: str = Field(default="UNTIS_TO_MIS")
    lesson_id: Optional[str] = None
    entity_type: str = Field(..., description="teacher, room, class, student, or lesson")
    error_type: str = Field(..., description="COLLISION, UNASSIGNED_ROOM, UNMAPPED_STUDENT, DUTY_PERIOD")
    details: str
    raw_payload: Dict[str, Any]


class QuarantineItemCreate(QuarantineItemBase):
    pass


class QuarantineResolutionPayload(BaseModel):
    status: str = Field(..., description="RESOLVED or IGNORED")
    resolved_override: Dict[str, Any] = Field(
        ...,
        description="Dictionary containing manual assignments (e.g. {'override_room_id': 204, 'override_staff_id': 102})"
    )


class QuarantineItemResponse(QuarantineItemBase):
    id: int
    status: str
    resolved_override: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuarantineSummaryStats(BaseModel):
    total_quarantined: int
    pending_count: int
    resolved_count: int
    ignored_count: int