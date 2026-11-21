import os
import uuid
from pathlib import Path
from typing import Tuple, Optional, Any, Union
from starlette.datastructures import UploadFile
from fastapi import HTTPException, status
from backend.core.config import settings
from backend.core.logging import logger

# Recognized magic byte signatures
MAGIC_BYTES = {
    "image/jpeg": [b"\xFF\xD8\xFF"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "audio/wav": [b"RIFF"],
    "audio/mpeg": [b"ID3", b"\xFF\xFB", b"\xFF\xF3", b"\xFF\xF2"]
}

ALLOWED_IMAGE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"]
}

ALLOWED_AUDIO_TYPES = {
    "audio/wav": [".wav"],
    "audio/mpeg": [".mp3"]
}

class FileValidator:
    """
    Validates uploaded media using binary magic bytes and size constraints.
    Protects against disguised executables and path traversal attacks.
    """

    @staticmethod
    def detect_mime_from_bytes(data: bytes) -> Optional[str]:
        """Inspects the leading bytes of a file to determine its actual MIME type."""
        for mime_type, signatures in MAGIC_BYTES.items():
            for sig in signatures:
                if data.startswith(sig):
                    # WAV files must also have WAVE in header bytes 8-12
                    if mime_type == "audio/wav":
                        if len(data) >= 12 and data[8:12] == b"WAVE":
                            return mime_type
                        continue
                    return mime_type
        return None

    @classmethod
    async def validate_image(cls, file: UploadFile) -> Tuple[bytes, str, str]:
        """
        Validates an uploaded image file:
        1. Checks size against MAX_IMAGE_SIZE_BYTES.
        2. Inspects magic bytes to ensure it is actually a JPEG or PNG.
        Returns: (file_bytes, detected_mime, secure_filename)
        """
        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded image is empty."
            )

        if file_size > settings.MAX_IMAGE_SIZE_BYTES:
            max_mb = settings.MAX_IMAGE_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image exceeds maximum allowed size of {max_mb}MB."
            )

        detected_mime = cls.detect_mime_from_bytes(content)
        if detected_mime not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported or corrupted image format. Only JPEG and PNG are allowed."
            )

        # Generate a safe, randomized storage filename
        ext = ALLOWED_IMAGE_TYPES[detected_mime][0]
        secure_filename = f"{uuid.uuid4().hex}{ext}"

        # Reset cursor for future reads if necessary
        await file.seek(0)
        return content, detected_mime, secure_filename

    @classmethod
    async def validate_audio(cls, file: UploadFile) -> Tuple[bytes, str, str]:
        """
        Validates an uploaded audio file:
        1. Checks size against MAX_AUDIO_SIZE_BYTES.
        2. Inspects magic bytes to ensure it is actually WAV or MP3.
        Returns: (file_bytes, detected_mime, secure_filename)
        """
        content = await file.read()
        file_size = len(content)

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded audio file is empty."
            )

        if file_size > settings.MAX_AUDIO_SIZE_BYTES:
            max_mb = settings.MAX_AUDIO_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio exceeds maximum allowed size of {max_mb}MB."
            )

        detected_mime = cls.detect_mime_from_bytes(content)
        if detected_mime not in ALLOWED_AUDIO_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported or corrupted audio format. Only WAV and MP3 are allowed."
            )

        ext = ALLOWED_AUDIO_TYPES[detected_mime][0]
        secure_filename = f"{uuid.uuid4().hex}{ext}"

        await file.seek(0)
        return content, detected_mime, secure_filename

    @staticmethod
    def save_file_to_disk(content: bytes, destination_path: Path) -> Path:
        """Saves validated binary content safely to disk."""
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(content)
        return destination_path
