import os
from pathlib import Path
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from backend.core.config import settings

router = APIRouter(prefix="/audio", tags=["Audio"])

@router.get("/{filename}")
async def get_audio_file(filename: str):
    """
    Serves generated TTS audio files securely.
    Sanitizes filenames to prevent path traversal attacks.
    """
    safe_filename = os.path.basename(filename)
    file_path = settings.audio_cache_dir / safe_filename

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found."
        )

    # Determine media type
    if safe_filename.endswith(".mp3"):
        media_type = "audio/mpeg"
    elif safe_filename.endswith(".wav"):
        media_type = "audio/wav"
    else:
        media_type = "application/octet-stream"

    return FileResponse(path=str(file_path), media_type=media_type)
