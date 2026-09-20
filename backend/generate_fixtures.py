# backend/generate_fixtures.py

import json
from pathlib import Path

FIXTURES_DIR = Path(__file__).resolve().parent / "tests" / "fixtures"
FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. ARBOR MOCK DATASET
# -------------------------------------------------------------
arbor_periods = [
    {"day_number": d, "period_number": p, "start_time": st, "end_time": et}
    for d in range(1, 6)
    for p, (st, et) in enumerate(
        [("09:00", "10:00"), ("10:15", "11:15"), ("11:30", "12:30"), ("13:30", "14:30"), ("14:45", "15:45")],
        start=1,
    )
]

arbor_teachers = [
    {"teacher_id": "TR_DM", "last_name": "Davies", "first_name": "Mark"},
    {"teacher_id": "TR_GR", "last_name": "Green", "first_name": "Rachel"},
    {"teacher_id": "TR_SG", "last_name": "Smith", "first_name": "Gareth"},
    {"teacher_id": "TR_TB", "last_name": "Taylor", "first_name": "Benjamin"},
    {"teacher_id": "TR_MP", "last_name": "Patel", "first_name": "Maya"},
    {"teacher_id": "TR_AG", "last_name": "Adams", "first_name": "George"},
]

arbor_classes = [
    {"class_code": "CL_7A", "description": "Year 7 Tutor Group A"},
    {"class_code": "CL_8A", "description": "Year 8 Tutor Group A"},
    {"class_code": "CL_9A", "description": "Year 9 Tutor Group A"},
]

arbor_rooms = [
    {"room_code": "R101", "description": "English Lab 1", "capacity": 30},
    {"room_code": "R102", "description": "Maths Studio 2", "capacity": 32},
    {"room_code": "R201", "description": "Science Lab A", "capacity": 28},
    {"room_code": "GYM", "description": "Sports Pavilion", "capacity": 60},
]

arbor_subjects = [
    {"subject_code": "ENG", "name": "English Language"},
    {"subject_code": "MAT", "name": "Mathematics"},
    {"subject_code": "SCI", "name": "Combined Science"},
    {"subject_code": "PE", "name": "Physical Education"},
    {"subject_code": "HIS", "name": "History"},
]

arbor_lessons = [
    {"lesson_id": "ARB_LES_101", "class_code": "CL_7A", "teacher_code": "TR_DM", "subject_code": "ENG", "periods_per_week": 3, "group_code": ""},
    {"lesson_id": "ARB_LES_102", "class_code": "CL_7A", "teacher_code": "TR_GR", "subject_code": "MAT", "periods_per_week": 3, "group_code": ""},
    {"lesson_id": "ARB_LES_103", "class_code": "CL_7A", "teacher_code": "TR_TB", "subject_code": "SCI", "periods_per_week": 2, "group_code": ""},
    {"lesson_id": "ARB_LES_104", "class_code": "CL_7A", "teacher_code": "TR_SG", "subject_code": "PE", "periods_per_week": 2, "group_code": "SG_PE_7A"},
    {"lesson_id": "ARB_LES_201", "class_code": "CL_8A", "teacher_code": "TR_MP", "subject_code": "HIS", "periods_per_week": 2, "group_code": ""},
]

arbor_slots = [
    {"lesson_id": "ARB_LES_101", "day_number": 1, "period_number": 1, "room_code": "R101"},
    {"lesson_id": "ARB_LES_101", "day_number": 3, "period_number": 4, "room_code": "R101"},
    {"lesson_id": "ARB_LES_101", "day_number": 4, "period_number": 5, "room_code": "R101"},
    {"lesson_id": "ARB_LES_102", "day_number": 2, "period_number": 2, "room_code": "R102"},
    {"lesson_id": "ARB_LES_102", "day_number": 3, "period_number": 1, "room_code": "R102"},
    {"lesson_id": "ARB_LES_102", "day_number": 5, "period_number": 5, "room_code": "R102"},
    {"lesson_id": "ARB_LES_103", "day_number": 2, "period_number": 3, "room_code": "R201"},
    {"lesson_id": "ARB_LES_103", "day_number": 5, "period_number": 1, "room_code": "R201"},
    {"lesson_id": "ARB_LES_104", "day_number": 3, "period_number": 2, "room_code": "GYM"},
    {"lesson_id": "ARB_LES_104", "day_number": 5, "period_number": 4, "room_code": "GYM"},
    {"lesson_id": "ARB_LES_201", "day_number": 1, "period_number": 5, "room_code": "R102"},
    {"lesson_id": "ARB_LES_201", "day_number": 4, "period_number": 2, "room_code": "R102"},
]

arbor_payload = {
    "source_mis": "ARBOR",
    "periods": arbor_periods,
    "teachers": arbor_teachers,
    "classes": arbor_classes,
    "rooms": arbor_rooms,
    "subjects": arbor_subjects,
    "lessons": arbor_lessons,
    "slots": arbor_slots,
}

# -------------------------------------------------------------
# 2. BROMCOM MOCK DATASET
# -------------------------------------------------------------
bromcom_periods = [
    {"day_number": d, "period_number": p, "start_time": st, "end_time": et}
    for d in range(1, 6)
    for p, (st, et) in enumerate(
        [("08:45", "09:45"), ("10:00", "11:00"), ("11:15", "12:15"), ("13:15", "14:15"), ("14:30", "15:30")],
        start=1,
    )
]

bromcom_teachers = [
    {"teacher_id": "BC_T1", "last_name": "Hawkins", "first_name": "Edward"},
    {"teacher_id": "BC_T2", "last_name": "Sinclair", "first_name": "Victoria"},
    {"teacher_id": "BC_T3", "last_name": "Chen", "first_name": "David"},
]

bromcom_classes = [
    {"class_code": "10B_ENG", "description": "Year 10 English Band B"},
    {"class_code": "10B_MAT", "description": "Year 10 Mathematics Band B"},
]

bromcom_rooms = [
    {"room_code": "E01", "description": "East Block 01", "capacity": 30},
    {"room_code": "W04", "description": "West Block 04", "capacity": 30},
]

bromcom_subjects = [
    {"subject_code": "ENGL", "name": "English Literature"},
    {"subject_code": "MATH", "name": "Higher Mathematics"},
]

bromcom_lessons = [
    {"lesson_id": "BC_LES_501", "class_code": "10B_ENG", "teacher_code": "BC_T1", "subject_code": "ENGL", "periods_per_week": 2, "group_code": ""},
    {"lesson_id": "BC_LES_502", "class_code": "10B_MAT", "teacher_code": "BC_T2", "subject_code": "MATH", "periods_per_week": 2, "group_code": ""},
]

bromcom_slots = [
    {"lesson_id": "BC_LES_501", "day_number": 1, "period_number": 2, "room_code": "E01"},
    {"lesson_id": "BC_LES_501", "day_number": 3, "period_number": 3, "room_code": "E01"},
    {"lesson_id": "BC_LES_502", "day_number": 2, "period_number": 4, "room_code": "W04"},
    {"lesson_id": "BC_LES_502", "day_number": 4, "period_number": 1, "room_code": "W04"},
]

bromcom_payload = {
    "source_mis": "BROMCOM",
    "periods": bromcom_periods,
    "teachers": bromcom_teachers,
    "classes": bromcom_classes,
    "rooms": bromcom_rooms,
    "subjects": bromcom_subjects,
    "lessons": bromcom_lessons,
    "slots": bromcom_slots,
}

# -------------------------------------------------------------
# 3. WRITE FILES
# -------------------------------------------------------------
arbor_path = FIXTURES_DIR / "mock_arbor_response.json"
bromcom_path = FIXTURES_DIR / "mock_bromcom_response.json"

with open(arbor_path, "w", encoding="utf-8") as f:
    json.dump(arbor_payload, f, indent=2)

with open(bromcom_path, "w", encoding="utf-8") as f:
    json.dump(bromcom_payload, f, indent=2)

print(f"Created: {arbor_path} ({len(arbor_slots)} slots, {len(arbor_teachers)} teachers)")
print(f"Created: {bromcom_path} ({len(bromcom_slots)} slots, {len(bromcom_teachers)} teachers)")