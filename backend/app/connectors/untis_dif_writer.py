# backend/app/connectors/untis_dif_writer.py

from typing import Any, Dict, List
import io
import zipfile


class UntisDifWriter:
    """Generates standard Untis DIF exchange files (GPU001 to GPU008)."""

    @staticmethod
    def _sanitize(val: Any) -> str:
        if val is None:
            return ""
        return str(val).replace('"', '""').strip()

    @staticmethod
    def generate_gpu001_periods(periods: List[Dict[str, Any]]) -> str:
        """GPU001: Bell schedule & periods. Format: Day, Period, StartTime, EndTime"""
        lines = []
        for p in periods:
            day = p.get("day_number", 1)
            period = p.get("period_number", 1)
            start = UntisDifWriter._sanitize(p.get("start_time", "09:00")).replace(":", "")
            end = UntisDifWriter._sanitize(p.get("end_time", "10:00")).replace(":", "")
            lines.append(f'{day},{period},"{start}","{end}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu001_subjects(subjects: List[Dict[str, Any]]) -> str:
        """GPU001 variant: Subject master records. Format: SubjectCode, Name"""
        lines = []
        for s in subjects:
            s_code = UntisDifWriter._sanitize(s.get("subject_code") or s.get("code") or s.get("id"))
            name = UntisDifWriter._sanitize(s.get("name") or s_code)
            lines.append(f'"{s_code}","{name}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu002_teachers(teachers: List[Dict[str, Any]]) -> str:
        """GPU002: Teacher master records. Format: ID, Surname, Forename"""
        lines = []
        for t in teachers:
            t_id = UntisDifWriter._sanitize(t.get("teacher_id") or t.get("code") or t.get("id"))
            surname = UntisDifWriter._sanitize(t.get("last_name") or t.get("surname") or t_id)
            forename = UntisDifWriter._sanitize(t.get("first_name") or t.get("forename") or "")
            lines.append(f'"{t_id}","{surname}","{forename}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu003_classes(classes: List[Dict[str, Any]]) -> str:
        """GPU003: Classes / Cohorts. Format: ClassName, LongName"""
        lines = []
        for c in classes:
            c_name = UntisDifWriter._sanitize(c.get("class_code") or c.get("name") or c.get("id"))
            long_name = UntisDifWriter._sanitize(c.get("description") or c_name)
            lines.append(f'"{c_name}","{long_name}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu004_rooms(rooms: List[Dict[str, Any]]) -> str:
        """GPU004: Rooms & capacities. Format: RoomCode, Name, Capacity"""
        lines = []
        for r in rooms:
            r_code = UntisDifWriter._sanitize(r.get("room_code") or r.get("name") or r.get("id"))
            name = UntisDifWriter._sanitize(r.get("description") or r_code)
            cap = int(r.get("capacity") or 30)
            lines.append(f'"{r_code}","{name}",{cap}')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu005_subjects(subjects: List[Dict[str, Any]]) -> str:
        """GPU005: Subject departments. Format: SubjectCode, Name"""
        lines = []
        for s in subjects:
            s_code = UntisDifWriter._sanitize(s.get("subject_code") or s.get("code") or s.get("id"))
            name = UntisDifWriter._sanitize(s.get("name") or s_code)
            lines.append(f'"{s_code}","{name}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu005_students(students: List[Dict[str, Any]]) -> str:
        """GPU005 variant: Student master records. Format: ID, Surname, Forename, Class"""
        lines = []
        for st in students:
            st_id = UntisDifWriter._sanitize(st.get("student_id") or st.get("id"))
            surname = UntisDifWriter._sanitize(st.get("last_name") or st.get("surname") or st_id)
            forename = UntisDifWriter._sanitize(st.get("first_name") or st.get("forename") or "")
            cohort = UntisDifWriter._sanitize(st.get("class_code") or st.get("cohort") or "")
            lines.append(f'"{st_id}","{surname}","{forename}","{cohort}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu007_lessons(lessons: List[Dict[str, Any]]) -> str:
        """GPU007: Course & Lesson Definitions.
        Format: LessonID, Class, Teacher, Subject, PeriodsPerWeek, StudentGroup
        """
        lines = []
        for les in lessons:
            les_id = UntisDifWriter._sanitize(les.get("lesson_id"))
            c_code = UntisDifWriter._sanitize(les.get("class_code"))
            t_code = UntisDifWriter._sanitize(les.get("teacher_code"))
            s_code = UntisDifWriter._sanitize(les.get("subject_code"))
            ppw = int(les.get("periods_per_week") or 1)
            group = UntisDifWriter._sanitize(les.get("group_code", ""))
            lines.append(f'"{les_id}","{c_code}","{t_code}","{s_code}",{ppw},"{group}"')
        return "\r\n".join(lines)

    @staticmethod
    def generate_gpu008_placements(slots: List[Dict[str, Any]]) -> str:
        """GPU008: Timetable Placements (Grid allocations).
        Format: LessonID, DayNumber (1=Mon), PeriodNumber, RoomCode
        """
        lines = []
        for slot in slots:
            les_id = UntisDifWriter._sanitize(slot.get("lesson_id"))
            day = int(slot.get("day_number") or 1)
            period = int(slot.get("period_number") or 1)
            r_code = UntisDifWriter._sanitize(slot.get("room_code", ""))
            lines.append(f'"{les_id}",{day},{period},"{r_code}"')
        return "\r\n".join(lines)

    @staticmethod
    def bundle_all_dif(master_catalog: Dict[str, Any]) -> Dict[str, str]:
        """Returns a dict mapping DIF file names to string content."""
        bundle: Dict[str, str] = {}
        if "periods" in master_catalog:
            bundle["GPU001.txt"] = UntisDifWriter.generate_gpu001_periods(master_catalog.get("periods", []))
        elif "subjects" in master_catalog:
            bundle["GPU001.txt"] = UntisDifWriter.generate_gpu001_subjects(master_catalog.get("subjects", []))

        if "teachers" in master_catalog:
            bundle["GPU002.txt"] = UntisDifWriter.generate_gpu002_teachers(master_catalog.get("teachers", []))
        if "classes" in master_catalog:
            bundle["GPU003.txt"] = UntisDifWriter.generate_gpu003_classes(master_catalog.get("classes", []))
        if "rooms" in master_catalog:
            bundle["GPU004.txt"] = UntisDifWriter.generate_gpu004_rooms(master_catalog.get("rooms", []))
        if "students" in master_catalog:
            bundle["GPU005.txt"] = UntisDifWriter.generate_gpu005_students(master_catalog.get("students", []))
        elif "subjects" in master_catalog and "GPU001.txt" not in bundle:
            bundle["GPU005.txt"] = UntisDifWriter.generate_gpu005_subjects(master_catalog.get("subjects", []))
        if "lessons" in master_catalog:
            bundle["GPU007.txt"] = UntisDifWriter.generate_gpu007_lessons(master_catalog.get("lessons", []))
        if "slots" in master_catalog:
            bundle["GPU008.txt"] = UntisDifWriter.generate_gpu008_placements(master_catalog.get("slots", []))
        return bundle

    def assemble_dif_zip(self, mis_payload: Dict[str, Any]) -> io.BytesIO:
        """Packages GPU001 through GPU008 into an in-memory ZIP archive."""
        zip_buffer = io.BytesIO()
        bundled_files = UntisDifWriter.bundle_all_dif(mis_payload)

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for filename, content in bundled_files.items():
                zf.writestr(filename, content.encode("utf-8"))

        zip_buffer.seek(0)
        return zip_buffer