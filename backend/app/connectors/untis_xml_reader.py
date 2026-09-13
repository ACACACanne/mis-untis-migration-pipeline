from pathlib import Path
from typing import Union
import xml.etree.ElementTree as ET

from app.schemas.untis_xml import (
    UntisGeneralInfo,
    UntisTimePeriod,
    UntisTeacher,
    UntisSubject,
    UntisRoom,
    UntisClass,
    UntisStudent,
    UntisLessonTime,
    UntisLesson,
    UntisParsedDataset,
)

NAMESPACE = {"u": "https://untis.at/untis/XmlInterface"}


class UntisXmlReader:
    """Parses and validates Untis XML 3.8 export files."""

    def __init__(self, source: Union[str, Path, bytes]):
        if isinstance(source, bytes):
            self.root = ET.fromstring(source)
        elif isinstance(source, (str, Path)):
            tree = ET.parse(str(source))
            self.root = tree.getroot()
        else:
            raise ValueError("Unsupported XML source type. Provide bytes, str, or Path.")

    def _get_text(self, elem: ET.Element, path: str, default: str = "") -> str:
        found = elem.find(f"u:{path}", NAMESPACE)
        if found is None:
            found = elem.find(path)
        return found.text.strip() if (found is not None and found.text) else default

    def _find_all(self, elem: ET.Element, tag_name: str) -> list[ET.Element]:
        found = elem.findall(f".//u:{tag_name}", NAMESPACE)
        if not found:
            found = elem.findall(f".//{tag_name}")
        return found

    def parse(self) -> UntisParsedDataset:
        return UntisParsedDataset(
            general=self._parse_general(),
            timeperiods=self._parse_timeperiods(),
            teachers=self._parse_teachers(),
            subjects=self._parse_subjects(),
            rooms=self._parse_rooms(),
            classes=self._parse_classes(),
            students=self._parse_students(),
            lessons=self._parse_lessons(),
        )

    def _parse_general(self) -> UntisGeneralInfo:
        gen_elem = self.root.find("u:general", NAMESPACE)
        if gen_elem is None:
            gen_elem = self.root.find("general")

        if gen_elem is None:
            return UntisGeneralInfo(
                school_name="Untis Schedule",
                school_year_begin="20250901",
                school_year_end="20260731",
            )

        return UntisGeneralInfo(
            school_name=self._get_text(gen_elem, "schoolname", "Untis Schedule"),
            school_year_begin=self._get_text(gen_elem, "schoolyearbegindate", "20250901"),
            school_year_end=self._get_text(gen_elem, "schoolyearenddate", "20260731"),
            term_name=self._get_text(gen_elem, "termname") or None,
            term_begin=self._get_text(gen_elem, "termbegindate") or None,
            term_end=self._get_text(gen_elem, "termenddate") or None,
        )

    def _parse_timeperiods(self) -> list[UntisTimePeriod]:
        periods = []
        for tp in self._find_all(self.root, "timeperiod"):
            periods.append(
                UntisTimePeriod(
                    id=tp.attrib.get("id", ""),
                    day=int(self._get_text(tp, "day", "1")),
                    period=int(self._get_text(tp, "period", "1")),
                    start_time=self._get_text(tp, "starttime", "0000"),
                    end_time=self._get_text(tp, "endtime", "0000"),
                )
            )
        return periods

    def _parse_teachers(self) -> list[UntisTeacher]:
        teachers = []
        for t in self._find_all(self.root, "teacher"):
            teachers.append(
                UntisTeacher(
                    id=t.attrib.get("id", ""),
                    surname=self._get_text(t, "surname", ""),
                    forename=self._get_text(t, "forename", "") or None,
                    idnumber=self._get_text(t, "idnumber") or None,
                )
            )
        return teachers

    def _parse_subjects(self) -> list[UntisSubject]:
        subjects = []
        for s in self._find_all(self.root, "subject"):
            subjects.append(
                UntisSubject(
                    id=s.attrib.get("id", ""),
                    long_name=self._get_text(s, "longname", s.attrib.get("id", "")),
                    forecolor=self._get_text(s, "forecolor", "#000000"),
                    backcolor=self._get_text(s, "backcolor", "#FFFFFF"),
                )
            )
        return subjects

    def _parse_rooms(self) -> list[UntisRoom]:
        rooms = []
        for r in self._find_all(self.root, "room"):
            rooms.append(
                UntisRoom(
                    id=r.attrib.get("id", ""),
                    long_name=self._get_text(r, "longname") or None,
                )
            )
        return rooms

    def _parse_classes(self) -> list[UntisClass]:
        classes = []
        for c in self._find_all(self.root, "class"):
            classes.append(
                UntisClass(
                    id=c.attrib.get("id", ""),
                    long_name=self._get_text(c, "longname") or None,
                )
            )
        return classes

    def _parse_students(self) -> list[UntisStudent]:
        students = []
        for s in self._find_all(self.root, "student"):
            s_id = s.attrib.get("id", "")
            class_elem = s.find("u:student_class", NAMESPACE)
            if class_elem is None:
                class_elem = s.find("student_class")
            base_class = class_elem.attrib.get("id") if class_elem is not None else None

            students.append(
                UntisStudent(
                    id=s_id,
                    forename=self._get_text(s, "forename", ""),
                    surname=self._get_text(s, "surname", ""),
                    gender=self._get_text(s, "gender") or None,
                    idnumber=self._get_text(s, "idnumber") or None,
                    base_class=base_class,
                )
            )
        return students

    def _parse_lessons(self) -> list[UntisLesson]:
        lessons = []
        for l in self._find_all(self.root, "lesson"):
            l_id = l.attrib.get("id", "")
            periods = int(self._get_text(l, "periods", "1"))

            sub_elem = l.find("u:lesson_subject", NAMESPACE) or l.find("lesson_subject")
            subject_id = sub_elem.attrib.get("id") if sub_elem is not None else None

            tea_elem = l.find("u:lesson_teacher", NAMESPACE) or l.find("lesson_teacher")
            teacher_id = tea_elem.attrib.get("id") if tea_elem is not None else None

            cls_elem = l.find("u:lesson_classes", NAMESPACE) or l.find("lesson_classes")
            class_ids = cls_elem.attrib.get("id", "").split() if cls_elem is not None else []

            sg_elem = l.find("u:lesson_studentgroups", NAMESPACE) or l.find("lesson_studentgroups")
            studentgroup_id = sg_elem.attrib.get("id") if sg_elem is not None else None

            # Student allocations
            st_elem = l.find("u:lesson_students", NAMESPACE) or l.find("lesson_students")
            raw_students = st_elem.attrib.get("id", "").strip() if st_elem is not None else ""
            assigned_students = []
            if raw_students:
                assigned_students = [
                    f"ST_{part.strip()}" for part in raw_students.split("ST_") if part.strip()
                ]

            times = []
            for tm in (l.findall(".//u:time", NAMESPACE) or l.findall(".//time")):
                day_val = self._get_text(tm, "assigned_day")
                period_val = self._get_text(tm, "assigned_period")
                if day_val and period_val:
                    times.append(
                        UntisLessonTime(
                            assigned_day=int(day_val),
                            assigned_period=int(period_val),
                            start_time=self._get_text(tm, "assigned_starttime") or None,
                            end_time=self._get_text(tm, "assigned_endtime") or None,
                        )
                    )

            lessons.append(
                UntisLesson(
                    id=l_id,
                    periods=periods,
                    subject_id=subject_id,
                    teacher_id=teacher_id,
                    class_ids=class_ids,
                    studentgroup_id=studentgroup_id,
                    effective_begin=self._get_text(l, "effectivebegindate") or None,
                    effective_end=self._get_text(l, "effectiveenddate") or None,
                    assigned_students=assigned_students,
                    times=times,
                )
            )
        return lessons