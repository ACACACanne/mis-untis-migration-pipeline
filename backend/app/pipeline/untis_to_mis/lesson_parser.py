from typing import Any, Dict, List, Tuple
from app.schemas.untis_xml import UntisLesson, UntisTimePeriod
from app.pipeline.untis_to_mis.timeperiod_mapper import TimePeriodMapper


class LessonParser:
    """Decomposes Untis master lessons into discrete, scheduleable timetable units."""

    DUTY_OR_NON_CONTACT_CODES = {"SU_NCC", "DUTY", "PPA", "COVER"}

    def __init__(self, timeperiods: List[UntisTimePeriod]):
        self.period_lookup = TimePeriodMapper.build_lookup_table(timeperiods)

    def parse_lessons(
        self, lessons: List[UntisLesson]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Processes lesson definitions.
        Returns:
            (valid_slots, quarantine_candidates)
        """
        valid_slots = []
        quarantine_candidates = []

        for lesson in lessons:
            # 1. Non-contact / duty lessons without classes
            if not lesson.class_ids:
                if lesson.subject_id in self.DUTY_OR_NON_CONTACT_CODES or not lesson.subject_id:
                    for t in lesson.times:
                        quarantine_candidates.append({
                            "lesson_id": lesson.id,
                            "entity_type": "lesson",
                            "error_type": "DUTY_PERIOD",
                            "details": f"Duty/non-contact slot {lesson.subject_id} with teacher {lesson.teacher_id} requires manual room/supervision mapping.",
                            "raw_payload": lesson.model_dump(),
                        })
                    continue

            # 2. Iterate each scheduled occurrence
            for t in lesson.times:
                time_meta = self.period_lookup.get(
                    (t.assigned_day, t.assigned_period),
                    {
                        "start_time": TimePeriodMapper.format_time_string(t.start_time or "0900"),
                        "end_time": TimePeriodMapper.format_time_string(t.end_time or "1000"),
                    },
                )

                # Expand multi-class cohorts (e.g. Banded PE across 7A and 7B)
                for class_code in lesson.class_ids:
                    slot_entry = {
                        "untis_lesson_id": lesson.id,
                        "class_code": class_code,
                        "subject_code": lesson.subject_id,
                        "teacher_id": lesson.teacher_id,
                        "studentgroup_id": lesson.studentgroup_id,
                        "day_of_week": t.assigned_day,
                        "period_number": t.assigned_period,
                        "start_time": time_meta["start_time"],
                        "end_time": time_meta["end_time"],
                        "assigned_students": lesson.assigned_students,
                    }

                    # Flag missing teachers for quarantine
                    if not lesson.teacher_id:
                        quarantine_candidates.append({
                            "lesson_id": lesson.id,
                            "entity_type": "teacher",
                            "error_type": "UNASSIGNED_TEACHER",
                            "details": f"Lesson {lesson.id} ({lesson.subject_id}) has no assigned instructor.",
                            "raw_payload": slot_entry,
                        })
                    else:
                        valid_slots.append(slot_entry)

        return valid_slots, quarantine_candidates