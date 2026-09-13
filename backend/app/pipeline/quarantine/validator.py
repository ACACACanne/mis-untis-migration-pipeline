from typing import Any, Dict, List, Set, Tuple
from sqlalchemy.orm import Session
from app.models.quarantine import QuarantineItem
from app.models.key_registry import KeyRegistry


class QuarantineValidator:
    """Performs collision detection, room validation, and key registry reconciliation."""

    def __init__(self, db: Session):
        self.db = db

    def check_and_isolate_anomalies(
        self, slots: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[QuarantineItem]]:
        clean_slots: List[Dict[str, Any]] = []
        quarantine_entries: List[QuarantineItem] = []

        seen_teacher_slots: Set[Tuple[str, int, int]] = set()
        seen_room_slots: Set[Tuple[str, int, int]] = set()

        # Load existing registry identifiers
        known_teachers = {
            k.untis_id for k in self.db.query(KeyRegistry).filter_by(entity_type="teacher").all()
        }

        for slot in slots:
            lesson_id = slot.get("untis_lesson_id")
            teacher_id = slot.get("teacher_id")
            room_code = slot.get("room_code")
            day = slot.get("day_of_week")
            period = slot.get("period_number")

            # 1. Unregistered / Unmapped Teacher
            if teacher_id and known_teachers and teacher_id not in known_teachers:
                item = QuarantineItem(
                    sync_direction="UNTIS_TO_MIS",
                    lesson_id=lesson_id,
                    entity_type="teacher",
                    error_type="UNMAPPED_TEACHER",
                    details=f"Teacher '{teacher_id}' in lesson '{lesson_id}' is not mapped in the Key Registry.",
                    raw_payload=slot,
                    status="PENDING",
                )
                quarantine_entries.append(item)
                continue

            # 2. Teacher Scheduling Clash (Same teacher scheduled in two places at the same time)
            if teacher_id and day and period:
                teacher_key = (teacher_id, day, period)
                if teacher_key in seen_teacher_slots:
                    item = QuarantineItem(
                        sync_direction="UNTIS_TO_MIS",
                        lesson_id=lesson_id,
                        entity_type="teacher",
                        error_type="COLLISION",
                        details=f"Teacher collision: '{teacher_id}' is scheduled multiple times at Day {day}, Period {period}.",
                        raw_payload=slot,
                        status="PENDING",
                    )
                    quarantine_entries.append(item)
                    continue
                seen_teacher_slots.add(teacher_key)

            # 3. Room Clash (Same room booked by multiple lessons simultaneously)
            if room_code and day and period:
                room_key = (room_code, day, period)
                if room_key in seen_room_slots:
                    item = QuarantineItem(
                        sync_direction="UNTIS_TO_MIS",
                        lesson_id=lesson_id,
                        entity_type="room",
                        error_type="ROOM_COLLISION",
                        details=f"Room collision: Room '{room_code}' is double-booked at Day {day}, Period {period}.",
                        raw_payload=slot,
                        status="PENDING",
                    )
                    quarantine_entries.append(item)
                    continue
                seen_room_slots.add(room_key)

            # If clean, pass through
            clean_slots.append(slot)

        return clean_slots, quarantine_entries