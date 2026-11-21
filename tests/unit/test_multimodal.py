import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.safety.file_validator import FileValidator

client = TestClient(app)

# Sample valid binary byte signatures for testing
VALID_PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
VALID_JPEG_BYTES = b"\xFF\xD8\xFF\xE0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00\xFF\xDB\x00C\x00\xFF\xD9"
VALID_WAV_BYTES = b"RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x10\xb1\x02\x00\x02\x00\x10\x00data\x00\x00\x00\x00"

def test_file_validator_magic_bytes():
    """Verify that magic bytes correctly identify file types and reject fakes."""
    assert FileValidator.detect_mime_from_bytes(VALID_PNG_BYTES) == "image/png"
    assert FileValidator.detect_mime_from_bytes(VALID_JPEG_BYTES) == "image/jpeg"
    assert FileValidator.detect_mime_from_bytes(VALID_WAV_BYTES) == "audio/wav"

    # Fake file test: plain text named as an image
    fake_txt_bytes = b"Hello, this is just plain text content!"
    assert FileValidator.detect_mime_from_bytes(fake_txt_bytes) is None

def test_multimodal_empty_request_rejected():
    """Verify that submitting no text and no files results in 400 Bad Request."""
    response = client.post("/chat", data={})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

def test_multimodal_fake_image_rejected():
    """Verify that an invalid file disguised as an image is rejected with 400."""
    fake_file = io.BytesIO(b"Not an actual image binary")
    response = client.post(
        "/chat",
        data={"message": "Look at this image"},
        files={"image": ("test.jpg", fake_file, "image/jpeg")}
    )
    assert response.status_code == 400
    assert "Unsupported or corrupted image" in response.json()["detail"]

def test_multimodal_image_plus_text():
    """Verify that a valid image combined with text is processed cleanly."""
    image_io = io.BytesIO(VALID_PNG_BYTES)
    response = client.post(
        "/chat",
        data={"message": "I drew this calming picture."},
        files={"image": ("calm.png", image_io, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_image"] is True
    assert data["modality"] == "multimodal"
    assert len(data["assistant_message"]) > 0

def test_multimodal_image_only():
    """Verify that an image-only submission works without explicit text."""
    image_io = io.BytesIO(VALID_PNG_BYTES)
    response = client.post(
        "/chat",
        files={"image": ("scenery.png", image_io, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_image"] is True
    assert data["modality"] == "image"

def test_multimodal_audio_plus_text():
    """Verify audio transcription and processing."""
    audio_io = io.BytesIO(VALID_WAV_BYTES)
    response = client.post(
        "/chat",
        data={"message": "Here is my voice note:"},
        files={"audio": ("voice.wav", audio_io, "audio/wav")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["audio_transcript"] is not None
    assert data["modality"] == "multimodal"

def test_multimodal_all_combined():
    """Verify Text + Image + Audio combined in one single request."""
    image_io = io.BytesIO(VALID_PNG_BYTES)
    audio_io = io.BytesIO(VALID_WAV_BYTES)
    response = client.post(
        "/chat",
        data={"message": "This is everything together."},
        files={
            "image": ("drawing.png", image_io, "image/png"),
            "audio": ("voice.wav", audio_io, "audio/wav")
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["has_image"] is True
    assert data["audio_transcript"] is not None
    assert data["modality"] == "multimodal"
