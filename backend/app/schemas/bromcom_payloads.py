from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BromcomClassBase(BaseModel):
    ClassCode: str = Field(..., description="Bromcom unique class code e.g., 10/Ar1")
    ClassName: str
    SubjectCode: str
    YearGroup: Optional[str] = None


class BromcomClassCreate(BromcomClassBase):
    pass


class BromcomClassResponse(BromcomClassBase):
    ClassId: int
    model_config = ConfigDict(from_attributes=True)


class BromcomTimetableSlot(BaseModel):
    SlotId: int
    DayNumber: int = Field(..., ge=1, le=10, description="Supports 1-week or 2-week cycles")
    PeriodNumber: int = Field(..., ge=1, le=20)
    StartTime: str = Field(..., description="HH:MM:SS format")
    EndTime: str = Field(..., description="HH:MM:SS format")


class BromcomScheduleAssignment(BaseModel):
    ClassId: int
    StaffId: Optional[int] = None
    RoomId: Optional[int] = None
    DayNumber: int
    PeriodNumber: int
    StartDate: str = Field(..., description="YYYY-MM-DD")
    EndDate: str = Field(..., description="YYYY-MM-DD")


class BromcomCurriculumEnrollment(BaseModel):
    ClassId: int
    StudentIds: List[int]
    EffectiveFrom: str
    EffectiveTo: Optional[str] = None