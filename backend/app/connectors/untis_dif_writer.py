import csv
import io
from typing import List, Dict, Any


class UntisDifWriter:
    """Generates Untis GPU standard DIF/CSV export tables from normalized master records."""

    @staticmethod
    def _render_csv(rows: List[List[Any]]) -> str:
        output = io.StringIO()
        writer = csv.writer(
            output,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_ALL,
            lineterminator="\r\n",
        )
        writer.writerows(rows)
        return output.getvalue()

    @classmethod
    def generate_gpu001_subjects(cls, subjects: List[Dict[str, Any]]) -> str:
        """GPU001.txt: Subjects table [SubjectID, LongName, AlternateCode, TextColor, BackColor]."""
        rows = [
            [
                s.get("subject_code", ""),
                s.get("name", ""),
                s.get("short_name", ""),
                s.get("text_color", "#000000"),
                s.get("back_color", "#FFFFFF"),
            ]
            for s in subjects
        ]
        return cls._render_csv(rows)

    @classmethod
    def generate_gpu002_teachers(cls, teachers: List[Dict[str, Any]]) -> str:
        """GPU002.txt: Teachers table [TeacherID, Surname, Forename, Title, MiscID]."""
        rows = [
            [
                t.get("staff_code", ""),
                t.get("surname", ""),
                t.get("forename", ""),
                t.get("title", ""),
                t.get("national_id", ""),
            ]
            for t in teachers
        ]
        return cls._render_csv(rows)

    @classmethod
    def generate_gpu003_classes(cls, classes: List[Dict[str, Any]]) -> str:
        """GPU003.txt: Classes/Cohorts table [ClassID, FullName, Dept, YearGroup]."""
        rows = [
            [
                c.get("class_code", ""),
                c.get("name", ""),
                c.get("department", ""),
                c.get("year_group", ""),
            ]
            for c in classes
        ]
        return cls._render_csv(rows)

    @classmethod
    def generate_gpu004_rooms(cls, rooms: List[Dict[str, Any]]) -> str:
        """GPU004.txt: Physical rooms table [RoomID, LongName, Capacity]."""
        rows = [
            [
                r.get("room_code", ""),
                r.get("name", ""),
                r.get("capacity", 30),
            ]
            for r in rooms
        ]
        return cls._render_csv(rows)

    @classmethod
    def generate_gpu005_students(cls, students: List[Dict[str, Any]]) -> str:
        """GPU005.txt: Pupils table [StudentID, Surname, Forename, Gender, DateOfBirth, PrimaryClass]."""
        rows = [
            [
                s.get("student_id", ""),
                s.get("surname", ""),
                s.get("forename", ""),
                s.get("gender", ""),
                s.get("dob", ""),
                s.get("base_class", ""),
            ]
            for s in students
        ]
        return cls._render_csv(rows)

    @classmethod
    def bundle_all_dif(cls, master_data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, str]:
        """Bundles all tables into a dictionary of filenames mapped to file content."""
        return {
            "GPU001.txt": cls.generate_gpu001_subjects(master_data.get("subjects", [])),
            "GPU002.txt": cls.generate_gpu002_teachers(master_data.get("teachers", [])),
            "GPU003.txt": cls.generate_gpu003_classes(master_data.get("classes", [])),
            "GPU004.txt": cls.generate_gpu004_rooms(master_data.get("rooms", [])),
            "GPU005.txt": cls.generate_gpu005_students(master_data.get("students", [])),
        }