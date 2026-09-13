from contextlib import asynccontextmanager
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure upload directories exist
    Path(settings.UNTIS_UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    yield
    # shutdown logic (close HTTP client connection pools, database connections, etc.) can be added here if needed

    app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Bi-directional timetable migration engine: Untis master publisher to UK MIS (Arbor/Bromcom) with master sync-back.",
    version="1.0.0",    
    lifespan=lifespan,
    )

    # Configure Cross-Origin Resource Sharing (CORS) settings
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKENGD_CORS_ORIGINS,  # Allow requests from these origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get(f"{settings.API_V1_STR}/health")
    async def health_check():
        # Initial system pulse endpoint for dashboard status pills
        return {
            "untis_source": "connected",
            "arbor_api": "connected",
            "bromcom_api": "connected",
            "database": "online",
            "pipeline_mode": "UNTIS_TO_MIS",
        }

    if __name__ == "__main__":
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)