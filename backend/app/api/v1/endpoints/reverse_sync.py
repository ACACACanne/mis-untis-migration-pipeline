# backend/app/api/v1/endpoints/reverse_sync.py

import json
from typing import Any, Dict
from fastapi import APIRouter, Depends, Query, Response, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.pipeline.mis_to_untis.master_extractor import MisToUntisExtractor

router = APIRouter()


@router.get("/preview", response_model=Dict[str, Any])
async def preview_mis_timetable(
    target_mis: str = Query("ARBOR", pattern="^(ARBOR|BROMCOM)$"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieves live or simulated MIS timetable metadata for inspection."""
    try:
        extractor = MisToUntisExtractor(db, target_mis=target_mis)
        raw = await extractor.fetch_raw_schedule()
        return {
            "source_mis": target_mis.upper(),
            "periods_count": len(raw.get("periods", [])),
            "teachers_count": len(raw.get("teachers", [])),
            "classes_count": len(raw.get("classes", [])),
            "rooms_count": len(raw.get("rooms", [])),
            "subjects_count": len(raw.get("subjects", [])),
            "lessons_count": len(raw.get("lessons", [])),
            "slots_count": len(raw.get("slots", [])),
        }
    except Exception as exc:
        return {
            "source_mis": target_mis.upper(),
            "periods_count": 25,
            "teachers_count": 6,
            "classes_count": 3,
            "rooms_count": 4,
            "subjects_count": 5,
            "lessons_count": 5,
            "slots_count": 12,
            "note": f"Fallback dataset loaded: {str(exc)}",
        }


@router.post("/upload-synthetic")
async def upload_synthetic_mis_file(
    target_mis: str = Query("ARBOR", pattern="^(ARBOR|BROMCOM)$"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Parses an uploaded synthetic or exported MIS JSON file and runs it through quarantine."""
    try:
        content = await file.read()
        payload = json.loads(content.decode("utf-8"))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file format: {str(exc)}")

    extractor = MisToUntisExtractor(db, target_mis=target_mis)
    clean_schedule, anomalies = extractor.validate_and_quarantine(payload)

    return {
        "status": "success",
        "filename": file.filename,
        "source_mis": target_mis.upper(),
        "periods_count": len(clean_schedule.get("periods", [])),
        "teachers_count": len(clean_schedule.get("teachers", [])),
        "classes_count": len(clean_schedule.get("classes", [])),
        "rooms_count": len(clean_schedule.get("rooms", [])),
        "subjects_count": len(clean_schedule.get("subjects", [])),
        "lessons_count": len(clean_schedule.get("lessons", [])),
        "slots_count": len(clean_schedule.get("slots", [])),
        "quarantined_count": len(anomalies),
    }


@router.get("/export-dif")
async def export_untis_dif_archive(
    target_mis: str = Query("ARBOR", pattern="^(ARBOR|BROMCOM)$"),
    db: Session = Depends(get_db),
):
    """Generates the GPU001-GPU008 Untis DIF ZIP archive."""
    extractor = MisToUntisExtractor(db, target_mis=target_mis)
    _, zip_bytes = await extractor.execute_export_pipeline()

    filename = f"Untis_Complete_{target_mis.upper()}.zip"
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )