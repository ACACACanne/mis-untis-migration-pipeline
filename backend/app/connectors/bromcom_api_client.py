# backend/app/connectors/bromcom_api_client.py

import json
from pathlib import Path
from typing import Any, Dict
import httpx
from app.core.config import settings


class BromcomApiClient:
    """Async client for Bromcom Cloud API with fixture fallback."""

    def __init__(self):
        self.base_url = (getattr(settings, "BROMCOM_BASE_URL", None) or "https://cloudapi.bromcom.com/v1").rstrip("/")
        self.api_key = getattr(settings, "BROMCOM_API_KEY", "mock-bromcom-key") or "mock-bromcom-key"
        self.school_id = str(getattr(settings, "BROMCOM_SCHOOL_ID", 12345))
        self.headers = {
            "ApiKey": self.api_key,
            "SchoolId": self.school_id,
            "Accept": "application/json",
        }

    async def check_connection(self) -> bool:
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return True
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/health", headers=self.headers)
                return res.status_code == 200
        except Exception:
            return False

    async def extract_complete_timetable(self) -> Dict[str, Any]:
        """Pulls Bromcom timetable schedules, falling back to fixtures if unavailable."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return self._load_fixture_or_fallback()

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.base_url}/timetables/active", headers=self.headers)
                return res.json()
        except Exception:
            return self._load_fixture_or_fallback()

    def _load_fixture_or_fallback(self) -> Dict[str, Any]:
        fixture_path = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures" / "mock_bromcom_response.json"
        if fixture_path.exists():
            try:
                with open(fixture_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

        periods = [
            {"day_number": d, "period_number": p, "start_time": st, "end_time": et}
            for d in range(1, 6)
            for p, (st, et) in enumerate(
                [("08:45", "09:45"), ("10:00", "11:00"), ("11:15", "12:15"), ("13:15", "14:15"), ("14:30", "15:30")],
                start=1,
            )
        ]

        teachers = [
            {"teacher_id": "BC_T1", "last_name": "Hawkins", "first_name": "Edward"},
            {"teacher_id": "BC_T2", "last_name": "Sinclair", "first_name": "Victoria"},
            {"teacher_id": "BC_T3", "last_name": "Chen", "first_name": "David"},
        ]

        classes = [
            {"class_code": "10B_ENG", "description": "Year 10 English Band B"},
            {"class_code": "10B_MAT", "description": "Year 10 Mathematics Band B"},
        ]

        rooms = [
            {"room_code": "E01", "description": "East Block 01", "capacity": 30},
            {"room_code": "W04", "description": "West Block 04", "capacity": 30},
        ]

        subjects = [
            {"subject_code": "ENGL", "name": "English Literature"},
            {"subject_code": "MATH", "name": "Higher Mathematics"},
        ]

        lessons = [
            {"lesson_id": "BC_LES_501", "class_code": "10B_ENG", "teacher_code": "BC_T1", "subject_code": "ENGL", "periods_per_week": 2, "group_code": ""},
            {"lesson_id": "BC_LES_502", "class_code": "10B_MAT", "teacher_code": "BC_T2", "subject_code": "MATH", "periods_per_week": 2, "group_code": ""},
        ]

        slots = [
            {"lesson_id": "BC_LES_501", "day_number": 1, "period_number": 2, "room_code": "E01"},
            {"lesson_id": "BC_LES_501", "day_number": 3, "period_number": 3, "room_code": "E01"},
            {"lesson_id": "BC_LES_502", "day_number": 2, "period_number": 4, "room_code": "W04"},
            {"lesson_id": "BC_LES_502", "day_number": 4, "period_number": 1, "room_code": "W04"},
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

    async def schedule_assignment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Schedules a class assignment in Bromcom."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return {"status": "success", "assignment_id": payload.get("id", 201), "data": payload}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.post(f"{self.base_url}/timetables/assignments", json=payload, headers=self.headers)
            res.raise_for_status()
            return res.json()

    async def update_schedule_assignment(self, slot_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Updates an existing Bromcom schedule slot."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return {"status": "success", "assignment_id": slot_id, "data": payload}
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.put(f"{self.base_url}/timetables/assignments/{slot_id}", json=payload, headers=self.headers)
            res.raise_for_status()
            return res.json()

    async def delete_schedule_assignment(self, slot_id: int) -> bool:
        """Deletes a schedule assignment from Bromcom."""
        if getattr(settings, "ENVIRONMENT", "development") == "development" or "mock" in self.api_key.lower():
            return True
        async with httpx.AsyncClient(timeout=10.0) as client:
            res = await client.delete(f"{self.base_url}/timetables/assignments/{slot_id}", headers=self.headers)
            return res.status_code in (200, 204)