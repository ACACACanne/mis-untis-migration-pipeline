from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class UntisGeneralInfo(BaseModel):
    school_name: str = Field(..., description="Untis school entity name")
    school_year_begin: str = Field(..., description="YYYYMMDD format")
    school_year_end: str = Field(..., description="YYYYMMDD format")
    term_name: Optional[str] = None
    term_begin: Optional[str] = None
    term_end: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UntisTimePeriod(BaseModel):
    id: str = Field(..., description="Period identifier e.g., TP_1")
    day: int = Field(..., ge=1, le=7, description="Day of the week (1=Monday)")
    period: int = Field(..., ge=1, le=20, description="Period slot number")
    start_time: str = Field(..., description="HHMM format e.g., 0900")
    end_time: str = Field(..., description="HHMM format e.g., 1000")

    model_config = ConfigDict(from_attributes=True)


class UntisTeacher(BaseModel):
    id: str = Field(..., description="Untis internal ID e.g., TR_DM")
    surname: str
    forename: Optional[str] = ""
    idnumber: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UntisSubject(BaseModel):
    id: str = Field(..., description="Untis subject code e.g., SU_En")
    long_name: str
    forecolor: Optional[str] = "#000000"
    backcolor: Optional[str] = "#FFFFFF"

    model_config = ConfigDict(from_attributes=True)


class UntisRoom(BaseModel):
    id: str = Field(..., description="Room identifier e.g., RM_7B")
    long_name: Optional[str] = None
    capacity: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UntisClass(BaseModel):
    id: str = Field(..., description="Class or cohort code e.g., CL_7A, CL_10")
    long_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UntisStudent(BaseModel):
    id: str = Field(..., description="Untis internal student ID e.g., ST_Barbara Baldwin")
    forename: str
    surname: str
    gender: Optional[str] = None
    idnumber: Optional[str] = Field(None, description="MIS UPN or national pupil identifier")
    base_class: Optional[str] = Field(None, description="Primary registration tutor group")

    model_config = ConfigDict(from_attributes=True)


class UntisLessonTime(BaseModel):
    assigned_day: int = Field(..., ge=1, le=7)
    assigned_period: int = Field(..., ge=1, le=20)
    start_time: Optional[str] = None
    end_time: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UntisLesson(BaseModel):
    id: str = Field(..., description="Lesson element ID e.g., LS_100")
    periods: int = Field(1, description="Periods per week count")
    subject_id: Optional[str] = Field(None, description="Null indicates duty/NCC slot")
    teacher_id: Optional[str] = None
    class_ids: List[str] = Field(default_factory=list)
    studentgroup_id: Optional[str] = None
    effective_begin: Optional[str] = None
    effective_end: Optional[str] = None
    assigned_students: List[str] = Field(default_factory=list)
    times: List[UntisLessonTime] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class UntisParsedDataset(BaseModel):
    general: UntisGeneralInfo
    timeperiods: List[UntisTimePeriod]
    teachers: List[UntisTeacher]
    subjects: List[UntisSubject]
    rooms: List[UntisRoom]
    classes: List[UntisClass]
    students: List[UntisStudent]
    lessons: List[UntisLesson]

    model_config = ConfigDict(from_attributes=True)