from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from backend.services.safety.cleanup_service import cleanup_service
from backend.core.config import settings

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

class CleanupRequest(BaseModel):
    max_age_hours: int = Field(default=24, ge=1, le=168, description="Max age in hours of files to retain")

class CleanupResponse(BaseModel):
    message: str
    files_purged: int

class StorageStatsResponse(BaseModel):
    uploads_count: int
    audio_cache_count: int

@router.post("/cleanup", response_model=CleanupResponse)
async def trigger_cleanup(payload: CleanupRequest) -> CleanupResponse:
    """Manually triggers purging of temporary media files exceeding retention period."""
    purged = cleanup_service.cleanup_expired_files(max_age_hours=payload.max_age_hours)
    return CleanupResponse(
        message="Cleanup executed successfully.",
        files_purged=purged
    )

@router.get("/storage", response_model=StorageStatsResponse)
async def get_storage_stats() -> StorageStatsResponse:
    """Returns file counts in temporary uploads and audio cache directories."""
    uploads_count = sum(1 for p in settings.uploads_dir.iterdir() if p.is_file() and p.name != ".gitkeep")
    audio_count = sum(1 for p in settings.audio_cache_dir.iterdir() if p.is_file() and p.name != ".gitkeep")
    return StorageStatsResponse(
        uploads_count=uploads_count,
        audio_cache_count=audio_count
    )
