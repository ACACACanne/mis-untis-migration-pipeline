from typing import Any, Dict, List, Optional
import httpx
from app.core.config import settings


class ArborApiClient:
    """Async HTTP client for interacting with the Arbor REST API."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        app_id: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.base_url = (base_url or settings.ARBOR_API_BASE_URL).rstrip("/")
        self.app_id = app_id or settings.ARBOR_APP_ID
        self.api_key = api_key or settings.ARBOR_API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Application-Id": self.app_id,
            "X-Application-Key": self.api_key,
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
        """Health check pulse against Arbor status endpoint."""
        try:
            return await self._request("GET", "system/status")
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}

    async def get_staff(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "staff")

    async def get_rooms(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "rooms")

    async def get_teaching_groups(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "teaching-groups")

    async def get_timetable_slots(self) -> List[Dict[str, Any]]:
        return await self._request("GET", "timetable-slots")

    async def create_teaching_group(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "teaching-groups", data=payload)

    async def create_session(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "sessions", data=payload)

    async def patch_session(self, session_id: int, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("PATCH", f"sessions/{session_id}", data=payload)

    async def delete_session(self, session_id: int) -> Dict[str, Any]:
        return await self._request("DELETE", f"sessions/{session_id}")

    async def enroll_students(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", "teaching-group-memberships", data=payload)