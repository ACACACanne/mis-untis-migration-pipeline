from pathlib import Path
from typing import List, Optional, Union
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

    def _find_child(self, elem: ET.Element, tag_name: str) -> Optional[ET.Element]:
        """Safely locates an immediate child element matching namespaced or plain tags."""
        found = elem.find(f"u:{tag_name}", NAMESPACE)
        if found is not None:
            return found

        found = elem.find(tag_name)
        if found is not None:
            return found

        target = tag_name.lower().replace("_", "")
        for child in elem:
            local_tag = child.tag.split("}")[-1].lower().replace("_", "")
            if local_tag == target:
                return child

        return None

    def _find_first_child(self, elem: ET.Element, candidate_tags: List[str]) -> Optional[ET.Element]:
        """Iterates candidate tag names and returns the first matching element."""
        for tag in candidate_tags:
            child = self._find_child(elem, tag)
            if child is not None:
                return child
        return None

    def _get_text(self, elem: ET.Element, tag_name: str, default: str = "") -> str:
        child = self._find_child(elem, tag_name)
        if child is not None and child.text and child.text.strip():
            return child.text.strip()
        return default

    def _get_element_value(
        self, elem: ET.Element, candidate_names: List[str], default: str = ""
    ) -> str:
        """
        Extracts value by prioritizing child element text, then child attributes,
        and finally element-level attributes.
        """
        # 1. Child elements (<longname>English</longname>)
        for name in candidate_names:
            child = self._find_child(elem, name)
            if child is not None:
                if child.text and child.text.strip():
                    return child.text.strip()
                for attr_key in ("value", "name", "color", "val"):
                    if attr_key in child.attrib and child.attrib[attr_key].strip():
                        return child.attrib[attr_key].strip()

        # 2. Element attributes (<subject longname="English" ...>)
        for name in candidate_names:
            if name in elem.attrib and elem.attrib[name].strip():
                return elem.attrib[name].strip()
            target = name.lower().replace("_", "")
            for k, v in elem.attrib.items():
                if k.lower().replace("_", "") == target and v.strip():
                    return v.strip()

        return default

    def _find_all(self, elem: ET.Element, tag_name: str) -> List[ET.Element]:
        found = elem.findall(f".//u:{tag_name}", NAMESPACE)
        if not found:
            found = elem.findall(f".//{tag_name}")
        if not found:
            found = [
                child for child in elem if child.tag.split("}")[-1].lower() == tag_name.lower()
            ]
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
        gen_elem = self._find_first_child(self.root, ["general"])
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

    def _parse_timeperiods(self) -> List[UntisTimePeriod]:
        periods = []
        container = self._find_first_child(self.root, ["timeperiods"])
        search_root = container if container is not None else self.root

        for tp in self._find_all(search_root, "timeperiod"):
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

    def _parse_teachers(self) -> List[UntisTeacher]:
        teachers = []
        container = self._find_first_child(self.root, ["teachers"])
        search_root = container if container is not None else self.root

        for t in self._find_all(search_root, "teacher"):
            teachers.append(
                UntisTeacher(
                    id=t.attrib.get("id", ""),
                    surname=self._get_text(t, "surname", ""),
                    forename=self._get_text(t, "forename", "") or None,
                    idnumber=self._get_text(t, "idnumber") or None,
                )
            )
        return teachers

    def _parse_subjects(self) -> List[UntisSubject]:
        subjects = []
        container = self._find_first_child(self.root, ["subjects"])
        search_root = container if container is not None else self.root

        for s in self._find_all(search_root, "subject"):
            s_id = s.attrib.get("id", "")
            if not s_id:
                continue

            long_name = self._get_element_value(
                s, ["longname", "long_name", "description"], default=""
            )
            if not long_name:
                long_name = s.attrib.get("name") or s_id

            forecolor = self._get_element_value(
                s, ["forecolor", "fore_color", "textcolor", "text_color"], default="#000000"
            )
            if forecolor and not forecolor.startswith("#") and len(forecolor) == 6:
                forecolor = f"#{forecolor}"

            backcolor = self._get_element_value(
                s, ["backcolor", "back_color", "bgcolor", "bg_color"], default="#FFFFFF"
            )
            if backcolor and not backcolor.startswith("#") and len(backcolor) == 6:
                backcolor = f"#{backcolor}"

            subjects.append(
                UntisSubject(
                    id=s_id,
                    long_name=long_name,
                    forecolor=forecolor,
                    backcolor=backcolor,
                )
            )
        return subjects

    def _parse_rooms(self) -> List[UntisRoom]:
        rooms = []
        container = self._find_first_child(self.root, ["rooms"])
        search_root = container if container is not None else self.root

        for r in self._find_all(search_root, "room"):
            long_name_elem = self._find_first_child(r, ["longname", "long_name", "name"])
            long_name = (
                long_name_elem.text.strip()
                if (long_name_elem is not None and long_name_elem.text)
                else None
            )
            rooms.append(
                UntisRoom(
                    id=r.attrib.get("id", ""),
                    long_name=long_name,
                )
            )
        return rooms

    def _parse_classes(self) -> List[UntisClass]:
        classes = []
        container = self._find_first_child(self.root, ["classes"])
        search_root = container if container is not None else self.root

        for c in self._find_all(search_root, "class"):
            long_name_elem = self._find_first_child(c, ["longname", "long_name", "name"])
            long_name = (
                long_name_elem.text.strip()
                if (long_name_elem is not None and long_name_elem.text)
                else None
            )
            classes.append(
                UntisClass(
                    id=c.attrib.get("id", ""),
                    long_name=long_name,
                )
            )
        return classes

    def _parse_students(self) -> List[UntisStudent]:
        students = []
        container = self._find_first_child(self.root, ["students"])
        search_root = container if container is not None else self.root

        for s in self._find_all(search_root, "student"):
            s_id = s.attrib.get("id", "")
            class_elem = self._find_first_child(s, ["student_class", "class"])
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

    def _parse_lessons(self) -> List[UntisLesson]:
        lessons = []
        container = self._find_first_child(self.root, ["lessons"])
        search_root = container if container is not None else self.root

        for l in self._find_all(search_root, "lesson"):
            l_id = l.attrib.get("id", "")
            periods = int(self._get_text(l, "periods", "1"))

            sub_elem = self._find_first_child(l, ["lesson_subject", "subject"])
            subject_id = sub_elem.attrib.get("id") if sub_elem is not None else None

            tea_elem = self._find_first_child(l, ["lesson_teacher", "teacher"])
            teacher_id = tea_elem.attrib.get("id") if tea_elem is not None else None

            cls_elem = self._find_first_child(l, ["lesson_classes", "classes"])
            class_ids = cls_elem.attrib.get("id", "").split() if cls_elem is not None else []

            sg_elem = self._find_first_child(l, ["lesson_studentgroups", "studentgroups"])
            studentgroup_id = sg_elem.attrib.get("id") if sg_elem is not None else None

            st_elem = self._find_first_child(l, ["lesson_students", "students"])
            raw_students = st_elem.attrib.get("id", "").strip() if st_elem is not None else ""
            assigned_students = []
            if raw_students:
                assigned_students = [
                    f"ST_{part.strip()}" for part in raw_students.split("ST_") if part.strip()
                ]

            times = []
            time_elements = l.findall(".//u:time", NAMESPACE)
            if not time_elements:
                time_elements = l.findall(".//time")

            for tm in time_elements:
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