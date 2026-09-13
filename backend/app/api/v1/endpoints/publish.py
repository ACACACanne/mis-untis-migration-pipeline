from typing import Any, Dict, cast
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.timetable_diff import TimetableDiff
from app.models.sync_audit import SyncAudit
from app.pipeline.untis_to_mis.mis_publisher import MisPublisher

router = APIRouter()


@router.post("", response_model=Dict[str, Any])
async def execute_publish(
    target_mis: str = Query("ARBOR", regex="^(ARBOR|BROMCOM)$"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    staged_diffs = (
        db.query(TimetableDiff)
        .filter(
            TimetableDiff.target_mis == target_mis.upper(),
            TimetableDiff.status == "STAGED",
        )
        .all()
    )

    if not staged_diffs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No staged diff records found for target MIS: {target_mis}",
        )

    publisher = MisPublisher(target_mis=target_mis)
    diff_payloads = [
        {
            "change_type": d.change_type,
            "mis_slot_id": d.staged_slot_payload.get("mis_slot_id"),
            "untis_lesson_id": d.untis_lesson_id,
            "slot_payload": d.staged_slot_payload,
        }
        for d in staged_diffs
    ]

    publish_result = await publisher.publish_diffs(diff_payloads)

    # Mark successfully committed records
    for diff in staged_diffs:
        setattr(diff, "status", "COMMITTED")
    

    # Log audit entry
    audit = SyncAudit(
        sync_direction="UNTIS_TO_MIS",
        status="COMPLETED" if publish_result["failed"] == 0 else "PARTIAL_FAILURE",
        total_records=len(staged_diffs),
        committed_records=publish_result["committed"],
        quarantined_records=publish_result["failed"],
        error_message=str(publish_result["errors"]) if publish_result["errors"] else None,
        completed_at=datetime.now(timezone.utc),
    )
    db.add(audit)
    db.commit()

    return {
        "status": "completed",
        "target_mis": target_mis,
        "committed_count": publish_result["committed"],
        "failed_count": publish_result["failed"],
        "errors": publish_result["errors"],
    }