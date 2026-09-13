from typing import Any, Dict, List, Optional
from app.connectors.arbor_api_client import ArborApiClient
from app.connectors.bromcom_api_client import BromcomApiClient


class MisPublisher:
    """Dispatches timetable diff modifications to Arbor or Bromcom APIs."""

    def __init__(self, target_mis: str = "ARBOR"):
        self.target_mis = target_mis.upper()
        self.arbor_client: Optional[ArborApiClient] = (
            ArborApiClient() if self.target_mis == "ARBOR" else None
        )
        self.bromcom_client: Optional[BromcomApiClient] = (
            BromcomApiClient() if self.target_mis == "BROMCOM" else None
        )

    async def publish_diffs(self, diff_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Iterates and applies CREATE, UPDATE, and DELETE diffs to target MIS endpoints."""
        results = {"committed": 0, "failed": 0, "errors": []}

        for diff in diff_entries:
            change_type = diff.get("change_type", "")
            payload = diff.get("slot_payload", {})
            mis_slot_id = diff.get("mis_slot_id")

            try:
                if self.target_mis == "ARBOR":
                    await self._publish_arbor(change_type, mis_slot_id, payload)
                elif self.target_mis == "BROMCOM":
                    await self._publish_bromcom(change_type, mis_slot_id, payload)

                results["committed"] += 1
            except Exception as exc:
                results["failed"] += 1
                results["errors"].append({
                    "slot_id": mis_slot_id,
                    "lesson_id": diff.get("untis_lesson_id"),
                    "error": str(exc),
                })

        return results

    async def _publish_arbor(
        self, change_type: str, slot_id: Any, payload: Dict[str, Any]
    ) -> None:
        if not self.arbor_client:
            raise RuntimeError("Arbor client is not initialized for this publisher instance.")

        if change_type == "CREATE":
            await self.arbor_client.create_session(payload)
        elif change_type == "UPDATE":
            if slot_id is None:
                raise ValueError("Cannot UPDATE an Arbor session without a valid slot_id.")
            await self.arbor_client.patch_session(int(slot_id), payload)
        elif change_type == "DELETE":
            if slot_id is None:
                raise ValueError("Cannot DELETE an Arbor session without a valid slot_id.")
            await self.arbor_client.delete_session(int(slot_id))

    async def _publish_bromcom(
        self, change_type: str, slot_id: Any, payload: Dict[str, Any]
    ) -> None:
        if not self.bromcom_client:
            raise RuntimeError("Bromcom client is not initialized for this publisher instance.")

        if change_type == "CREATE":
            await self.bromcom_client.schedule_assignment(payload)
        elif change_type == "UPDATE":
            if slot_id is None:
                raise ValueError("Cannot UPDATE a Bromcom assignment without a valid slot_id.")
            await self.bromcom_client.update_schedule_assignment(int(slot_id), payload)
        elif change_type == "DELETE":
            if slot_id is None:
                raise ValueError("Cannot DELETE a Bromcom assignment without a valid slot_id.")
            await self.bromcom_client.delete_schedule_assignment(int(slot_id))