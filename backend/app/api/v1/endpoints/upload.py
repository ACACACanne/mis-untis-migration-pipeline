from typing import Any, Dict
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.connectors.untis_xml_reader import UntisXmlReader
from app.pipeline.untis_to_mis.lesson_parser import LessonParser
from app.pipeline.quarantine.validator import QuarantineValidator
from app.models.sync_audit import SyncAudit

router = APIRouter()


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

    # Decompose lessons into schedule slots
    lesson_parser = LessonParser(parsed_data.timeperiods)
    valid_slots, lesson_quarantine = lesson_parser.parse_lessons(parsed_data.lessons)

    # Validate against collisions and registry mappings
    validator = QuarantineValidator(db)
    clean_slots, detected_anomalies = validator.check_and_isolate_anomalies(valid_slots)

    # Persist quarantine records
    all_quarantine_items = detected_anomalies
    for q_item in all_quarantine_items:
        db.add(q_item)

    # Record sync audit entry
    audit = SyncAudit(
        sync_direction="UNTIS_TO_MIS",
        status="STAGED",
        total_records=len(valid_slots),
        staged_records=len(clean_slots),
        quarantined_records=len(all_quarantine_items) + len(lesson_quarantine),
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
            "clean_slots_ready": len(clean_slots),
            "quarantined_count": len(all_quarantine_items) + len(lesson_quarantine),
        },
    }