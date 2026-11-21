import time
import os
from pathlib import Path
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.core.config import settings, BASE_DIR
from backend.core.logging import logger
from backend.database.models import ChatSession, Message, MediaMetadata

class CleanupService:
    """
    Manages sensitive file lifecycle, automated retention cleanup,
    and physical deletion of media files when sessions are deleted.
    """

    @classmethod
    def delete_file_safely(cls, file_path_str: Optional[str]) -> bool:
        """Deletes a single file from disk safely if it exists."""
        if not file_path_str:
            return False
        try:
            p = Path(file_path_str)
            if p.exists() and p.is_file():
                # Ensure the file is strictly inside the project storage directory (prevent path traversal)
                storage_root = (BASE_DIR / "storage").resolve()
                resolved_p = p.resolve()
                if str(resolved_p).startswith(str(storage_root)):
                    p.unlink(missing_ok=True)
                    logger.info(f"Safely purged temporary file: {p.name}")
                    return True
                else:
                    logger.warning(f"Refused to delete file outside storage root: {file_path_str}")
        except Exception as exc:
            logger.error(f"Error purging file {file_path_str}: {exc}")
        return False

    @classmethod
    def purge_session_media(cls, db: Session, session_id: str) -> int:
        """
        Deletes all uploaded media files and generated TTS audio files
        associated with a specific conversation session before DB deletion.
        Returns count of purged files.
        """
        purged_count = 0
        
        # 1. Find all uploaded media files for this session
        media_records = (
            db.query(MediaMetadata)
            .join(Message, MediaMetadata.message_id == Message.id)
            .filter(Message.session_id == session_id)
            .all()
        )
        for med in media_records:
            if cls.delete_file_safely(med.storage_path):
                purged_count += 1

        # 2. Find all generated TTS audio files for this session
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id, Message.tts_audio_path != None)
            .all()
        )
        for msg in messages:
            if cls.delete_file_safely(msg.tts_audio_path):
                purged_count += 1

        return purged_count

    @classmethod
    def cleanup_expired_files(cls, max_age_hours: int = 24) -> int:
        """
        Scans storage/uploads/ and storage/audio_cache/ and removes files older than max_age_hours.
        Returns total count of cleaned files.
        """
        now = time.time()
        max_age_seconds = max_age_hours * 3600
        purged = 0

        target_dirs = [settings.uploads_dir, settings.audio_cache_dir]
        for directory in target_dirs:
            if not directory.exists():
                continue
            for item in directory.iterdir():
                # Skip .gitkeep files
                if item.name == ".gitkeep" or not item.is_file():
                    continue
                file_age = now - item.stat().st_mtime
                if file_age > max_age_seconds:
                    try:
                        item.unlink(missing_ok=True)
                        purged += 1
                        logger.info(f"Retention policy: Cleaned expired file {item.name}")
                    except Exception as exc:
                        logger.error(f"Failed to clean expired file {item.name}: {exc}")

        return purged

cleanup_service = CleanupService()
