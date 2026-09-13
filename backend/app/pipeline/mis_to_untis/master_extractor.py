from typing import Any, Dict, List
from app.connectors.arbor_api_client import ArborApiClient
from app.connectors.bromcom_api_client import BromcomApiClient


class MisMasterExtractor:
    """Extracts master baseline records (staff, rooms, classes, students) from active MIS instances."""

    def __init__(self, target_mis: str = "ARBOR"):
        self.target_mis = target_mis.upper()
        self.arbor_client = ArborApiClient() if self.target_mis == "ARBOR" else None
        self.bromcom_client = BromcomApiClient() if self.target_mis == "BROMCOM" else None

    async def fetch_master_catalog(self) -> Dict[str, List[Dict[str, Any]]]:
        """Fetches and normalizes master records into a standard dictionary."""
        if self.target_mis == "ARBOR":
            return await self._extract_from_arbor()
        elif self.target_mis == "BROMCOM":
            return await self._extract_from_bromcom()
        else:
            raise ValueError(f"Unsupported target MIS: {self.target_mis}")

    async def _extract_from_arbor(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.arbor_client:
            raise RuntimeError("Arbor client is uninitialized.")

        raw_staff = await self.arbor_client.get_staff()
        raw_rooms = await self.arbor_client.get_rooms()
        raw_groups = await self.arbor_client.get_teaching_groups()

        teachers = [
            {
                "staff_code": s.get("short_code") or f"TR_{s.get('id')}",
                "surname": s.get("legal_last_name", ""),
                "forename": s.get("legal_first_name", ""),
                "title": s.get("title", ""),
                "national_id": s.get("ni_number", ""),
            }
            for s in raw_staff
        ]

        rooms = [
            {
                "room_code": r.get("room_code") or f"RM_{r.get('id')}",
                "name": r.get("room_name", ""),
                "capacity": r.get("capacity", 30),
            }
            for r in raw_rooms
        ]

        classes = [
            {
                "class_code": g.get("code", ""),
                "name": g.get("name", ""),
                "department": g.get("subject_name", ""),
                "year_group": g.get("year_group", ""),
            }
            for g in raw_groups
        ]

        return {
            "subjects": [],
            "teachers": teachers,
            "classes": classes,
            "rooms": rooms,
            "students": [],
        }

    async def _extract_from_bromcom(self) -> Dict[str, List[Dict[str, Any]]]:
        if not self.bromcom_client:
            raise RuntimeError("Bromcom client is uninitialized.")

        raw_staff = await self.bromcom_client.get_staff()
        raw_rooms = await self.bromcom_client.get_rooms()
        raw_classes = await self.bromcom_client.get_classes()

        teachers = [
            {
                "staff_code": s.get("StaffCode") or f"TR_{s.get('StaffId')}",
                "surname": s.get("LastName", ""),
                "forename": s.get("FirstName", ""),
                "title": s.get("Salutation", ""),
                "national_id": str(s.get("StaffId", "")),
            }
            for s in raw_staff
        ]

        rooms = [
            {
                "room_code": r.get("RoomCode") or f"RM_{r.get('RoomId')}",
                "name": r.get("RoomName", ""),
                "capacity": r.get("Capacity", 30),
            }
            for r in raw_rooms
        ]

        classes = [
            {
                "class_code": c.get("ClassCode", ""),
                "name": c.get("ClassName", ""),
                "department": c.get("SubjectCode", ""),
                "year_group": c.get("YearGroup", ""),
            }
            for c in raw_classes
        ]

        return {
            "subjects": [],
            "teachers": teachers,
            "classes": classes,
            "rooms": rooms,
            "students": [],
        }