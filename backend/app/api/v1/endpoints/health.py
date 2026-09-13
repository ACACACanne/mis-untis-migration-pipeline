from typing import Any, Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.connectors.arbor_api_client import ArborApiClient
from app.connectors.bromcom_api_client import BromcomApiClient

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
async def check_pipeline_health(db: Session = Depends(get_db)) -> Dict[str, Any]:
    # Check PostgreSQL connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    # Check external MIS connectivity
    arbor = ArborApiClient()
    arbor_status = await arbor.get_health()

    bromcom = BromcomApiClient()
    bromcom_status = await bromcom.get_health()

    return {
        "database": db_status,
        "arbor_api": arbor_status.get("status", "connected"),
        "bromcom_api": bromcom_status.get("status", "connected"),
        "active_mode": "UNTIS_TO_MIS",
    }