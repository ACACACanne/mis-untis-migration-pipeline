from typing import Any, Dict, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.timetable_diff import TimetableDiff
from app.pipeline.simulator.dry_run import PipelineSimulator

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]])
def get_staged_diffs(
    target_mis: str = Query("ARBOR", regex="^(ARBOR|BROMCOM)$"),
    status: str = Query("STAGED"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    diffs = (
        db.query(TimetableDiff)
        .filter(
            TimetableDiff.target_mis == target_mis.upper(),
            TimetableDiff.status == status.upper(),
        )
        .all()
    )

    return [
        {
            "id": d.id,
            "untis_lesson_id": d.untis_lesson_id,
            "day_number": d.day_number,
            "period_number": d.period_number,
            "change_type": d.change_type,
            "slot_payload": d.staged_slot_payload,
            "status": d.status,
            "created_at": d.created_at,
        }
        for d in diffs
    ]


@router.post("/dry-run", response_model=Dict[str, Any])
def run_dry_run_simulation(
    target_mis: str = Query("ARBOR", regex="^(ARBOR|BROMCOM)$"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    diffs = (
        db.query(TimetableDiff)
        .filter(
            TimetableDiff.target_mis == target_mis.upper(),
            TimetableDiff.status == "STAGED",
        )
        .all()
    )

    diff_dicts = [
        {
            "change_type": d.change_type,
            "untis_lesson_id": d.untis_lesson_id,
            "slot_payload": d.staged_slot_payload,
        }
        for d in diffs
    ]

    return PipelineSimulator.run_simulation(diff_dicts, target_mis=target_mis)