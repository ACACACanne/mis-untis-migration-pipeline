# backend/app/connectors/arbor_api_client.py

import json
from pathlib import Path
from typing import Any, Dict
import httpx
from app.core.config import settings


class ArborApiClient:
    """Async API client for Arbor REST API v1 with automatic fixture fallback."""

    def __init__(self):
        self.base_url = (getattr(settings, "ARBOR_BASE_URL", None) or "https://api.arbor.sc/v1").rstrip("/")
        self.api_key = getattr(settings, "ARBOR_API_KEY", "mock-arbor-key") or "mock-arbor-key"
        self.app_id = getattr(settings, "ARBOR_APP_ID", "mock-arbor-app") or "mock-arbor-app"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Application-ID": self.app_id,
            "Accept": "application/json",
        }

    async def check_connection(self) -> bool:
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return True
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/status", headers=self.headers)
                return res.status_code == 200
        except Exception:
            return False

    async def extract_complete_timetable(self) -> Dict[str, Any]:
        """Extracts timetable entities, falling back to local fixtures on network failure."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return self._load_fixture_or_fallback()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                periods = (await client.get(f"{self.base_url}/timetable-periods", headers=self.headers)).json()
                teachers = (await client.get(f"{self.base_url}/staff", headers=self.headers)).json()
                classes = (await client.get(f"{self.base_url}/academic-cohorts", headers=self.headers)).json()
                rooms = (await client.get(f"{self.base_url}/locations", headers=self.headers)).json()
                subjects = (await client.get(f"{self.base_url}/curriculum-subjects", headers=self.headers)).json()
                slots = (await client.get(f"{self.base_url}/timetable-slots", headers=self.headers)).json()

            return {
                "periods": periods.get("data", []),
                "teachers": teachers.get("data", []),
                "classes": classes.get("data", []),
                "rooms": rooms.get("data", []),
                "subjects": subjects.get("data", []),
                "slots": slots.get("data", []),
            }
        except Exception:
            return self._load_fixture_or_fallback()

    def _load_fixture_or_fallback(self) -> Dict[str, Any]:
        """Loads from tests/fixtures/mock_arbor_response.json or builds fallback dataset."""
        fixture_path = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / "mock_arbor_response.json"
        if fixture_path.exists():
            try:
                with open(fixture_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        # In-memory realistic dataset
        periods = [
            {"day_number": d, "period_number": p, "start_time": st, "end_time": et}
            for d in range(1, 6)
            for p, (st, et) in enumerate(
                [("09:00", "10:00"), ("10:15", "11:15"), ("11:30", "12:30"), ("13:30", "14:30"), ("14:45", "15:45")],
                start=1,
            )
        ]

        teachers = [
            {"teacher_id": "TR_DM", "last_name": "Davies", "first_name": "Mark"},
            {"teacher_id": "TR_GR", "last_name": "Green", "first_name": "Rachel"},
            {"teacher_id": "TR_SG", "last_name": "Smith", "first_name": "Gareth"},
            {"teacher_id": "TR_TB", "last_name": "Taylor", "first_name": "Benjamin"},
            {"teacher_id": "TR_MP", "last_name": "Patel", "first_name": "Maya"},
            {"teacher_id": "TR_AG", "last_name": "Adams", "first_name": "George"},
        ]

        classes = [
            {"class_code": "CL_7A", "description": "Year 7 Tutor Group A"},
            {"class_code": "CL_8A", "description": "Year 8 Tutor Group A"},
            {"class_code": "CL_9A", "description": "Year 9 Tutor Group A"},
        ]

        rooms = [
            {"room_code": "R101", "description": "English Lab 1", "capacity": 30},
            {"room_code": "R102", "description": "Maths Studio 2", "capacity": 32},
            {"room_code": "R201", "description": "Science Lab A", "capacity": 28},
            {"room_code": "GYM", "description": "Sports Pavilion", "capacity": 60},
        ]

        subjects = [
            {"subject_code": "ENG", "name": "English Language"},
            {"subject_code": "MAT", "name": "Mathematics"},
            {"subject_code": "SCI", "name": "Combined Science"},
            {"subject_code": "PE", "name": "Physical Education"},
            {"subject_code": "HIS", "name": "History"},
        ]

        lessons = [
            {"lesson_id": "ARB_LES_101", "class_code": "CL_7A", "teacher_code": "TR_DM", "subject_code": "ENG", "periods_per_week": 3, "group_code": ""},
            {"lesson_id": "ARB_LES_102", "class_code": "CL_7A", "teacher_code": "TR_GR", "subject_code": "MAT", "periods_per_week": 3, "group_code": ""},
            {"lesson_id": "ARB_LES_103", "class_code": "CL_7A", "teacher_code": "TR_TB", "subject_code": "SCI", "periods_per_week": 2, "group_code": ""},
            {"lesson_id": "ARB_LES_104", "class_code": "CL_7A", "teacher_code": "TR_SG", "subject_code": "PE", "periods_per_week": 2, "group_code": "SG_PE_7A"},
            {"lesson_id": "ARB_LES_201", "class_code": "CL_8A", "teacher_code": "TR_MP", "subject_code": "HIS", "periods_per_week": 2, "group_code": ""},
        ]

        slots = [
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

        return {
            "periods": periods,
            "teachers": teachers,
            "classes": classes,
            "rooms": rooms,
            "subjects": subjects,
            "lessons": lessons,
            "slots": slots,
        }

    async def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Creates an Arbor TimetableSlot / Session."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return {"status": "success", "id": payload.get("id", 101), "data": payload}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(f"{self.base_url}/timetable-slots", json=payload, headers=self.headers)
            res.raise_for_status()
            return res.json()

    async def patch_session(self, slot_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing Arbor TimetableSlot."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return {"status": "success", "id": slot_id, "data": payload}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.patch(f"{self.base_url}/timetable-slots/{slot_id}", json=payload, headers=self.headers)
            res.raise_for_status()
            return res.json()

    async def delete_session(self, slot_id: int) -> bool:
        """Removes a TimetableSlot from Arbor."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return True
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.delete(f"{self.base_url}/timetable-slots/{slot_id}", headers=self.headers)
            return res.status_code in (200, 204)