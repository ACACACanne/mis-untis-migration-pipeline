from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Untis to MIS Timetable Migration Pipeline"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/untis_mis_pipeline"

    # Target MIS Credentials
    ARBOR_API_BASE_URL: str = "https://api.arbor.sc/v1"
    ARBOR_APP_ID: str = "mock_arbor_app_id"
    ARBOR_API_KEY: str = "mock_arbor_secret_key"

    BROMCOM_API_BASE_URL: str = "https://cloudservice.bromcom.com/v1"
    BROMCOM_SCHOOL_ID: int = 10001
    BROMCOM_API_TOKEN: str = "mock_bromcom_bearer_token"

    # Untis Storage & Limits
    UNTIS_UPLOAD_DIR: str = "./uploads/untis"
    MAX_UPLOAD_SIZE_MB: int = 25

    # Security
    API_SECRET_KEY: str = "migration-pipeline-internal-secret-token"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Instantiate Settings outside the class block (no leading indentation)
settings = Settings()

# Ensure uploads directory exists on disk
Path(settings.UNTIS_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
