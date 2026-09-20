# backend/app/core/config.py

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Untis UK MIS Migration Bridge"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "dev-secret-key-change-in-production-12345"

    # CORS origins
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*",
    ]

    # Primary pipeline: Untis to UK MIS; Secondary: MIS to Untis reverse sync
    ACTIVE_MODE: str = "MIS_TO_UNTIS"

    # Database
    DATABASE_URL: str = "sqlite:///./untis_pipeline.db"

    # Target MIS Configuration
    ARBOR_BASE_URL: str = "https://api.arbor.sc/v1"
    ARBOR_API_KEY: str = "mock-arbor-key"
    ARBOR_APP_ID: str = "mock-arbor-app"

    BROMCOM_BASE_URL: str = "https://cloudapi.bromcom.com/v1"
    BROMCOM_API_KEY: str = "mock-bromcom-key"
    BROMCOM_SCHOOL_ID: int = 12345

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"


settings = Settings()

