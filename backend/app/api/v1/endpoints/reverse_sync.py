# backend/app/api/v1/endpoints/reverse_sync.py

import io
import zipfile
from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Query, Response, status

from app.pipeline.mis_to_untis.master_extractor import MisMasterExtractor
from app.pipeline.mis_to_untis.untis_formatter import UntisFormatter

router = APIRouter()


@router.get("/preview", response_model=Dict[str, Any])
async def preview_mis_master_catalog(
    target_mis: str = Query("ARBOR", pattern="^(ARBOR|BROMCOM)$"),
) -> Dict[str, Any]:
    """Pulls current staff, room, and class rosters from the target MIS for pre-sync review."""
    extractor = MisMasterExtractor(target_mis=target_mis)
    try:
        catalog = await extractor.fetch_master_catalog()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to fetch master records from {target_mis}: {str(exc)}",
        )

    return {
        "target_mis": target_mis,
        "teachers_count": len(catalog["teachers"]),
        "rooms_count": len(catalog["rooms"]),
        "classes_count": len(catalog["classes"]),
        "catalog": catalog,
    }


@router.get("/export-dif")
async def export_untis_dif_archive(
    target_mis: str = Query("ARBOR", pattern="^(ARBOR|BROMCOM)$"),
):
    """Fetches MIS master baseline records and exports a ZIP archive containing GPU001-GPU005 DIF files."""
    extractor = MisMasterExtractor(target_mis=target_mis)
    try:
        catalog = await extractor.fetch_master_catalog()
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to extract records for DIF export from {target_mis}: {str(exc)}",
        )

    dif_files = UntisFormatter.generate_dif_package(catalog)

    # Build in-memory zip archive containing GPU tables
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for filename, content in dif_files.items():
            zip_file.writestr(filename, content)

    zip_buffer.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=Untis_Master_{target_mis}.zip"}

    return Response(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers=headers,
    )