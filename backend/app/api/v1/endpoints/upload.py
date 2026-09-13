# backend/app/api/v1/endpoints/upload.py

from typing import Any, Callable, Dict, List
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.connectors.untis_xml_reader import UntisXmlReader
from app.pipeline.untis_to_mis.lesson_parser import LessonParser
from app.pipeline.untis_to_mis.diff_engine import DiffEngine
from app.pipeline.quarantine.validator import QuarantineValidator
from app.models.timetable_diff import TimetableDiff
from app.models.quarantine import QuarantineItem
from app.models.sync_audit import SyncAudit

try:
    from app.models.key_registry import KeyRegistry
except ImportError:
    KeyRegistry = None

router = APIRouter()


def _normalize_slot(slot: Any) -> Dict[str, Any]:
    """Ensures consistent dictionary formatting across Pydantic models, dicts, or ORM objects."""
    if isinstance(slot, dict):
        d = dict(slot)
    elif hasattr(slot, "model_dump"):
        d = slot.model_dump()
    elif hasattr(slot, "__dict__"):
        d = dict(slot.__dict__)
    else:
        d = {}

    lesson_id = (
        d.get("untis_lesson_id")
        or d.get("lesson_id")
        or getattr(slot, "untis_lesson_id", None)
        or getattr(slot, "lesson_id", None)
        or d.get("id")
        or ""
    )
    day = (
        d.get("day_of_week")
        or d.get("day_number")
        or d.get("day")
        or getattr(slot, "day_of_week", None)
        or getattr(slot, "day_number", None)
        or 1
    )
    period = (
        d.get("period_number")
        or d.get("period")
        or getattr(slot, "period_number", None)
        or getattr(slot, "period", 1)
    )
    teacher = (
        d.get("teacher_id")
        or d.get("teacher")
        or getattr(slot, "teacher_id", None)
        or ""
    )
    room = (
        d.get("room_id")
        or d.get("room")
        or getattr(slot, "room_id", None)
        or ""
    )
    subject = (
        d.get("subject_id")
        or d.get("subject")
        or getattr(slot, "subject_id", None)
        or ""
    )
    class_ids = (
        d.get("class_ids")
        or getattr(slot, "class_ids", [])
        or []
    )
    if isinstance(class_ids, str):
        class_ids = class_ids.split()

    class_code = (
        d.get("class_code")
        or getattr(slot, "class_code", None)
        or (class_ids[0] if class_ids else "")
    )
    studentgroup_id = (
        d.get("studentgroup_id")
        or getattr(slot, "studentgroup_id", None)
        or ""
    )
    assigned_students = (
        d.get("assigned_students")
        or getattr(slot, "assigned_students", [])
        or []
    )

    d.update({
        "untis_lesson_id": lesson_id,
        "day_of_week": int(day),
        "day_number": int(day),
        "period_number": int(period),
        "teacher_id": teacher,
        "room_id": room,
        "subject_id": subject,
        "subject_code": subject,
        "class_code": class_code,
        "class_ids": class_ids,
        "studentgroup_id": studentgroup_id,
        "assigned_students": assigned_students,
    })
    return d


def _build_key_resolver(db: Session, target_mis: str) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Resolves Untis IDs to MIS-specific identifiers using the KeyRegistry or identity fallback."""
    registry_map: Dict[tuple, Any] = {}
    if KeyRegistry:
        try:
            for reg in db.query(KeyRegistry).all():
                registry_map[(reg.entity_type, reg.untis_id)] = reg
        except Exception:
            pass

    def resolver(slot: Dict[str, Any]) -> Dict[str, Any]:
        res = dict(slot)
        teacher_id = slot.get("teacher_id") or ""
        room_id = slot.get("room_id") or ""
        class_code = slot.get("class_code") or ""
        group_id = slot.get("studentgroup_id") or ""

        # Map teacher
        teacher_reg = registry_map.get(("teacher", teacher_id))
        mis_staff = (
            (teacher_reg.arbor_id if target_mis == "ARBOR" else teacher_reg.bromcom_id)
            if teacher_reg else teacher_id
        ) or teacher_id

        # Map room
        room_reg = registry_map.get(("room", room_id))
        mis_room = (
            (room_reg.arbor_id if target_mis == "ARBOR" else room_reg.bromcom_id)
            if room_reg else room_id
        ) or room_id

        # Map class / cohort
        class_reg = registry_map.get(("class", class_code))
        mis_class = (
            (class_reg.arbor_id if target_mis == "ARBOR" else class_reg.bromcom_id)
            if class_reg else class_code
        ) or class_code

        res["day_of_week"] = slot.get("day_of_week")
        res["period_number"] = slot.get("period_number")
        res["mis_staff_id"] = mis_staff
        res["mis_room_id"] = mis_room
        res["mis_group_code"] = group_id or mis_class or "YEAR_COHORT"
        res["class_code"] = mis_class or class_code
        res["teacher_id"] = mis_staff
        res["room_code"] = mis_room
        res["room_id"] = mis_room
        return res

    return resolver


@router.post("", response_model=Dict[str, Any])
async def upload_untis_xml(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    if not file.filename or not file.filename.endswith(".xml"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only valid Untis XML documents (.xml) are accepted.",
        )

    content = await file.read()
    try:
        reader = UntisXmlReader(content)
        parsed_data = reader.parse()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to parse Untis XML: {str(exc)}",
        )

    # 1. Decompose master lessons into individual schedule slots
    lesson_parser = LessonParser(parsed_data.timeperiods)
    valid_slots, lesson_quarantine = lesson_parser.parse_lessons(parsed_data.lessons)

    # 2. Check for collisions and conflicts
    validator = QuarantineValidator(db)
    clean_slots, detected_anomalies = validator.check_and_isolate_anomalies(valid_slots)

    # 3. Pull previously resolved quarantine items to re-integrate remediated lessons
    resolved_overrides: Dict[str, Dict[str, Any]] = {}
    resolved_records = (
        db.query(QuarantineItem)
        .filter(QuarantineItem.status == "RESOLVED")
        .all()
    )
    for r in resolved_records:
        lesson_id = r.__dict__.get("lesson_id")
        resolved_override = r.__dict__.get("resolved_override")
        if lesson_id is not None and resolved_override is not None:
            resolved_overrides[lesson_id] = resolved_override

    unresolved_anomalies = []
    remediated_slots = []

    for item in detected_anomalies:
        lesson_id = getattr(item, "lesson_id", None)
        if lesson_id and lesson_id in resolved_overrides:
            override = resolved_overrides[lesson_id]
            raw = getattr(item, "raw_payload", {}) or {}
            slot_dict = _normalize_slot(raw)
            if override.get("override_mis_staff_id"):
                slot_dict["teacher_id"] = override["override_mis_staff_id"]
            if override.get("override_mis_room_id"):
                slot_dict["room_id"] = override["override_mis_room_id"]
            remediated_slots.append(slot_dict)
        else:
            unresolved_anomalies.append(item)

    # 4. Save new pending quarantine entries without duplicate creation
    for q_item in unresolved_anomalies:
        lesson_id = getattr(q_item, "lesson_id", None)
        error_type = getattr(q_item, "error_type", None)
        existing = db.query(QuarantineItem).filter(
            QuarantineItem.lesson_id == lesson_id,
            QuarantineItem.error_type == error_type,
            QuarantineItem.status.in_(["PENDING", "RESOLVED", "IGNORED"]),
        ).first()
        if not existing:
            db.add(q_item)

    final_clean_slots = [_normalize_slot(s) for s in clean_slots] + remediated_slots

    # 5. Compute and stage diffs for both target MIS options
    targets = ["ARBOR", "BROMCOM"]

    # Clear previous STAGED entries to prevent duplicate accumulation
    db.query(TimetableDiff).filter(
        TimetableDiff.target_mis.in_(targets),
        TimetableDiff.status == "STAGED",
    ).delete(synchronize_session=False)

    for target in targets:
        committed_slots = (
            db.query(TimetableDiff)
            .filter(
                TimetableDiff.target_mis == target,
                TimetableDiff.status == "COMMITTED",
            )
            .all()
        )
        existing_mis_slots = [
            {
                "slot_id": c.id,
                "day_number": c.day_number,
                "period_number": c.period_number,
                "group_code": (c.staged_slot_payload or {}).get("mis_group_code")
                or (c.staged_slot_payload or {}).get("class_code"),
                "staff_id": (c.staged_slot_payload or {}).get("mis_staff_id")
                or (c.staged_slot_payload or {}).get("teacher_id"),
                "room_id": (c.staged_slot_payload or {}).get("mis_room_id")
                or (c.staged_slot_payload or {}).get("room_id"),
            }
            for c in committed_slots
        ]

        resolver = _build_key_resolver(db, target)
        diff_results = DiffEngine.compute_diff(
            incoming_untis_slots=final_clean_slots,
            existing_mis_slots=existing_mis_slots,
            key_resolver=resolver,
        )

        for d_res in diff_results:
            diff_entry = TimetableDiff(
                target_mis=target,
                untis_lesson_id=d_res.get("untis_lesson_id") or "UNKNOWN",
                day_number=d_res.get("day_number") or 1,
                period_number=d_res.get("period_number") or 1,
                change_type=d_res.get("change_type") or "CREATE",
                staged_slot_payload=d_res.get("slot_payload") or {},
                status="STAGED",
            )
            db.add(diff_entry)

    # 6. Audit transaction log
    audit = SyncAudit(
        sync_direction="UNTIS_TO_MIS",
        status="STAGED",
        total_records=len(valid_slots),
        staged_records=len(final_clean_slots),
        quarantined_records=len(unresolved_anomalies),
    )
    db.add(audit)
    db.commit()

    return {
        "filename": file.filename,
        "school_name": parsed_data.general.school_name,
        "summary": {
            "periods_detected": len(parsed_data.timeperiods),
            "teachers_detected": len(parsed_data.teachers),
            "classes_detected": len(parsed_data.classes),
            "lessons_parsed": len(parsed_data.lessons),
            "clean_slots_ready": len(final_clean_slots),
            "quarantined_count": len(unresolved_anomalies),
        },
    }