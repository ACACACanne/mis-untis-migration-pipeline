from fastapi import APIRouter
from app.api.v1.endpoints import (
    health,
    upload,
    diff,
    publish,
    quarantine,
    reverse_sync,
    registry,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["System Health"])
api_router.include_router(upload.router, prefix="/upload", tags=["Untis XML Ingestion"])
api_router.include_router(diff.router, prefix="/diff", tags=["Timetable Diff & Pre-Flight"])
api_router.include_router(publish.router, prefix="/publish", tags=["MIS Publishing"])
api_router.include_router(quarantine.router, prefix="/quarantine", tags=["Quarantine Management"])
api_router.include_router(reverse_sync.router, prefix="/reverse-sync", tags=["Reverse Master Sync"])
api_router.include_router(registry.router, prefix="/registry", tags=["Key Registry"])