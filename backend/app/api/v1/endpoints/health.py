# backend/app/api/v1/endpoints/health.py

from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings
from app.connectors.arbor_api_client import ArborApiClient
from app.connectors.bromcom_api_client import BromcomApiClient

router = APIRouter()


@router.get("", response_model=Dict[str, str])
async def check_health(db: Session = Depends(get_db)):
    """System health endpoint. Guaranteed to return 200 OK with status strings."""
    # 1. Database Connectivity Check
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "offline"

    # 2. In local development or mock mode, report connected
    if getattr(settings, "ENVIRONMENT", "development") == "development":
        return {
            "database": db_status,
            "arbor_api": "connected",
            "bromcom_api": "connected",
        }

    # 3. Live Production Handshake (safely caught)
    arbor_status = "unreachable"
    try:
        arbor_client = ArborApiClient()
        if await arbor_client.check_connection():
            arbor_status = "connected"
    except Exception:
        arbor_status = "unreachable"

    bromcom_status = "unreachable"
    try:
        bromcom_client = BromcomApiClient()
        if await bromcom_client.check_connection():
            bromcom_status = "connected"
    except Exception:
        bromcom_status = "unreachable"

    return {
        "database": db_status,
        "arbor_api": arbor_status,
        "bromcom_api": bromcom_status,
    }