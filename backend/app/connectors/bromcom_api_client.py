from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings


class BromcomApiClient:
    """Async HTTP client for interacting with the Bromcom Cloud Services API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        school_id: Optional[int] = None,
        api_token: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.BROMCOM_API_BASE_URL).rstrip("/")
        self.school_id = school_id or settings.BROMCOM_SCHOOL_ID
        self.api_token = api_token or settings.BROMCOM_API_TOKEN
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_token}",
            "X-School-Id": str(self.school_id),
        }

    async def _request(
        self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
            )
            response.raise_for_status()
            return response.json()

    async def get_health(self) -> Dict[str, Any]:
        """Health check pulse against Bromcom status endpoint."""
        try:
            return await self._request("GET", "system/pulse")
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    async def get_staff(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "curriculum/staff")

    async def get_rooms(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "curriculum/rooms")

    async def get_classes(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "curriculum/classes")

    async def get_timetable_slots(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "curriculum/timetable-slots")

    async def create_class(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "curriculum/classes", data=payload)

    async def schedule_assignment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "curriculum/schedule-assignments", data=payload)

    async def update_schedule_assignment(self, slot_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("PUT", f"curriculum/schedule-assignments/{slot_id}", data=payload)

    async def delete_schedule_assignment(self, slot_id: int) -> Dict[str, Any]:
        return await self._request("DELETE", f"curriculum/schedule-assignments/{slot_id}")

    async def enroll_students(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "curriculum/enrollments", data=payload)