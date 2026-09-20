# backend/app/pipeline/mis_to_untis/master_extractor.py

from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session

from app.connectors.arbor_api_client import ArborApiClient
from app.connectors.bromcom_api_client import BromcomApiClient
from app.connectors.untis_dif_writer import UntisDifWriter
from app.models.quarantine import QuarantineItem
from app.models.sync_audit import SyncAudit


class MisToUntisExtractor:
    """Primary pipeline engine: pulls active MIS schedules and transforms them into Untis packages."""

    def __init__(self, db: Session, target_mis: str = "ARBOR"):
        self.db = db
        self.target_mis = target_mis.upper()
        self.dif_writer = UntisDifWriter()
        self.arbor_client = ArborApiClient()
        self.bromcom_client = BromcomApiClient()

    async def fetch_raw_schedule(self) -> Dict[str, Any]:
        if self.target_mis == "ARBOR":
            return await self.arbor_client.extract_complete_timetable()
        return await self.bromcom_client.extract_complete_timetable()

    def validate_and_quarantine(
        self, raw_schedule: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], List[QuarantineItem]]:
        anomalies: List[QuarantineItem] = []
        clean_slots: List[Dict[str, Any]] = []

        seen_staff_slots = set()
        seen_room_slots = set()

        lessons_map = {l["lesson_id"]: l for l in raw_schedule.get("lessons", [])}

        for slot in raw_schedule.get("slots", []):
            les_id = slot.get("lesson_id")
            day = slot.get("day_number")
            period = slot.get("period_number")
            room = slot.get("room_code")
            parent_les = lessons_map.get(les_id, {})
            teacher = parent_les.get("teacher_code")

            if not teacher:
                q = QuarantineItem(
                    sync_direction="MIS_TO_UNTIS",
                    lesson_id=les_id,
                    entity_type="teacher",
                    error_type="ORPHAN_SLOT",
                    details=f"MIS Slot {les_id} has no assigned teacher at Day {day}, Period {period}.",
                    raw_payload=slot,
                    status="PENDING",
                )
                anomalies.append(q)
                continue

            staff_key = (teacher, day, period)
            if staff_key in seen_staff_slots:
                q = QuarantineItem(
                    sync_direction="MIS_TO_UNTIS",
                    lesson_id=les_id,
                    entity_type="teacher",
                    error_type="COLLISION",
                    details=f"Staff collision in MIS: '{teacher}' double-booked at Day {day}, Period {period}.",
                    raw_payload=slot,
                    status="PENDING",
                )
                anomalies.append(q)
                continue
            seen_staff_slots.add(staff_key)

            if room:
                room_key = (room, day, period)
                if room_key in seen_room_slots:
                    q = QuarantineItem(
                        sync_direction="MIS_TO_UNTIS",
                        lesson_id=les_id,
                        entity_type="room",
                        error_type="COLLISION",
                        details=f"Room collision in MIS: '{room}' double-booked at Day {day}, Period {period}.",
                        raw_payload=slot,
                        status="PENDING",
                    )
                    anomalies.append(q)
                    continue
                seen_room_slots.add(room_key)

            clean_slots.append(slot)

        for a in anomalies:
            self.db.add(a)

        clean_schedule = dict(raw_schedule)
        clean_schedule["slots"] = clean_slots
        return clean_schedule, anomalies

    async def execute_export_pipeline(self) -> Tuple[Dict[str, Any], bytes]:
        raw_schedule = await self.fetch_raw_schedule()
        clean_schedule, anomalies = self.validate_and_quarantine(raw_schedule)

        audit = SyncAudit(
            sync_direction=f"{self.target_mis}_TO_UNTIS",
            status="COMPLETED" if not anomalies else "PARTIAL",
            total_records=len(raw_schedule.get("slots", [])),
            staged_records=len(clean_schedule.get("slots", [])),
            quarantined_records=len(anomalies),
        )
        self.db.add(audit)
        self.db.commit()

        zip_stream = self.dif_writer.assemble_dif_zip(clean_schedule)
        summary = {
            "source_mis": self.target_mis,
            "periods_exported": len(clean_schedule.get("periods", [])),
            "teachers_exported": len(clean_schedule.get("teachers", [])),
            "classes_exported": len(clean_schedule.get("classes", [])),
            "rooms_exported": len(clean_schedule.get("rooms", [])),
            "subjects_exported": len(clean_schedule.get("subjects", [])),
            "lessons_exported": len(clean_schedule.get("lessons", [])),
            "slots_exported": len(clean_schedule.get("slots", [])),
            "quarantined_anomalies": len(anomalies),
        }
        return summary, zip_stream.getvalue()