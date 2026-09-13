from typing import Any, Dict, List, Tuple
from app.schemas.untis_xml import UntisLesson, UntisStudent


class OptionBlockProcessor:
    """Manages elective option bands and pupil memberships for target MIS rosters."""

    @staticmethod
    def identify_option_blocks(
        lessons: List[UntisLesson],
    ) -> Dict[Tuple[int, int], List[UntisLesson]]:
        """Finds concurrent elective lessons running at the identical day and period slot."""
        slots: Dict[Tuple[int, int], List[UntisLesson]] = {}
        for lesson in lessons:
            if not lesson.studentgroup_id:
                continue
            for t in lesson.times:
                key = (t.assigned_day, t.assigned_period)
                slots.setdefault(key, []).append(lesson)

        return {slot: grouped for slot, grouped in slots.items() if len(grouped) > 1}

    @staticmethod
    def build_enrollment_payload(
        lesson: UntisLesson,
        student_directory: Dict[str, UntisStudent],
        target_mis: str = "ARBOR",
    ) -> Dict[str, Any]:
        """Maps Untis elective student assignments to MIS curriculum enrollment payloads."""
        resolved_students = []
        for s_id in lesson.assigned_students:
            student = student_directory.get(s_id)
            if student:
                resolved_students.append({
                    "untis_student_id": s_id,
                    "student_name": f"{student.forename} {student.surname}".strip(),
                    "idnumber": student.idnumber,
                    "base_class": student.base_class,
                    "elective_group": lesson.studentgroup_id,
                    "subject": lesson.subject_id,
                })

        primary_class = lesson.class_ids[0] if lesson.class_ids else "YEAR_COHORT"

        if target_mis.upper() == "ARBOR":
            return {
                "group_identifier": lesson.studentgroup_id or f"{primary_class}/{lesson.subject_id}",
                "mis_group_identifier": lesson.studentgroup_id or f"{primary_class}/{lesson.subject_id}",
                "subject_code": lesson.subject_id,
                "academic_cohort": primary_class,
                "class_cohort": primary_class,
                "student_count": len(resolved_students),
                "students": resolved_students,
                "enrolled_students": resolved_students,
            }
        else:  # BROMCOM
            return {
                "ClassCode": lesson.studentgroup_id or f"{primary_class}_{lesson.subject_id}",
                "SubjectCode": lesson.subject_id,
                "YearGroup": primary_class,
                "StudentCount": len(resolved_students),
                "EnrolledStudents": resolved_students,
            }