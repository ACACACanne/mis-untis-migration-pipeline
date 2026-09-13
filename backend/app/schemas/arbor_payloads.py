from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class ArborTeachingGroupBase(BaseModel):
    code: str = Field(..., description="Arbor group identifier e.g., 7A/En")
    name: str = Field(..., description="Display label e.g., Year 7 English Class A")
    academic_year_id: int
    subject_id: Optional[int] = None


class ArborTeachingGroupCreate(ArborTeachingGroupBase):
    pass


class ArborTeachingGroupResponse(ArborTeachingGroupBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ArborTimetableSlot(BaseModel):
    id: Optional[int] = None
    day_of_week: int = Field(..., ge=1, le=7)
    period_number: int = Field(..., ge=1, le=20)
    start_time: str = Field(..., description="HH:MM format e.g., 09:00")
    end_time: str = Field(..., description="HH:MM format e.g., 10:00")
    time_cycle_id: Optional[int] = 1


class ArborSessionCreate(BaseModel):
    teaching_group_id: int
    staff_id: Optional[int] = Field(None, description="Arbor staff person ID")
    room_id: Optional[int] = Field(None, description="Arbor physical room location ID")
    timetable_slot_id: Optional[int] = None
    start_datetime: str = Field(..., description="ISO 8601 string: YYYY-MM-DDTHH:MM:SS")
    end_datetime: str = Field(..., description="ISO 8601 string: YYYY-MM-DDTHH:MM:SS")
    is_cover: bool = False


class ArborSessionResponse(ArborSessionCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class ArborStudentGroupEnrollment(BaseModel):
    teaching_group_id: int
    student_ids: List[int]
    start_date: str = Field(..., description="YYYY-MM-DD")
    end_date: Optional[str] = Field(None, description="YYYY-MM-DD")