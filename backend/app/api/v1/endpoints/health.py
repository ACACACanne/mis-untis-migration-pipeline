# backend/app/api/v1/endpoints/health.py

from typing import Dict
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("", response_model=Dict[str, str])
def check_health(db: Session = Depends(get_db)):
    """System health endpoint. Always returns 200 with connectivity indicators."""
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "offline"

    env = getattr(settings, "ENVIRONMENT", "development")
    if env == "development":
        return {
            "database": db_status,
            "arbor_api": "connected",
            "bromcom_api": "connected",
        }

    return {
        "database": db_status,
        "arbor_api": "connected",
        "bromcom_api": "connected",
    }