# backend/app/core/config.py

import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings

# Project root directory for local file persistence
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    PROJECT_NAME: str = "Untis UK MIS Bridge"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'timetable.db'}")

    # File storage paths
    UNTIS_UPLOAD_DIR: str = os.getenv("UNTIS_UPLOAD_DIR", str(BASE_DIR / "uploads" / "untis"))
    EXPORT_DIR: str = os.getenv("EXPORT_DIR", str(BASE_DIR / "exports"))

    # Allowed CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "https://<your-project-name>.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "*",
    ]

    # Active Pipeline Mode
    ACTIVE_MODE: str = "MIS_TO_UNTIS"

    # Arbor Configuration
    ARBOR_BASE_URL: str = os.getenv("ARBOR_BASE_URL", "https://api.arbor.sc/v1")
    ARBOR_API_KEY: str = os.getenv("ARBOR_API_KEY", "mock-arbor-key")
    ARBOR_APP_ID: str = os.getenv("ARBOR_APP_ID", "mock-arbor-app")

    # Bromcom Configuration
    BROMCOM_BASE_URL: str = os.getenv("BROMCOM_BASE_URL", "https://cloudapi.bromcom.com/v1")
    BROMCOM_API_KEY: str = os.getenv("BROMCOM_API_KEY", "mock-bromcom-key")
    BROMCOM_SCHOOL_ID: int = int(os.getenv("BROMCOM_SCHOOL_ID", "12345"))

    class Config:
        case_sensitive = True
        extra = "allow"


settings = Settings()

