import io
import time
import logging
from pathlib import Path
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.config import settings
from backend.core.logging import SanitizingFilter
from backend.services.safety.cleanup_service import cleanup_service

client = TestClient(app)

VALID_PNG_BYTES = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"

def test_security_headers():
    """Verify that essential HTTP security headers are enforced on all responses."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert "x-xss-protection" in response.headers

def test_session_deletion_purges_physical_media():
    """
    Verify Privacy Requirement (Right to be Forgotten):
    Deleting a conversation session must delete associated database records
    AND physically delete uploaded media files from disk.
    """
    image_io = io.BytesIO(VALID_PNG_BYTES)
    
    # Files before upload
    before_files = set(settings.uploads_dir.glob("*.png"))

    # 1. Upload an image to start a session
    resp = client.post(
        "/chat",
        data={"message": "Temporary image for privacy test"},
        files={"image": ("privacy_test.png", image_io, "image/png")}
    )
    assert resp.status_code == 200
    session_id = resp.json()["session_id"]

    # 2. Identify the exact newly created file
    after_files = set(settings.uploads_dir.glob("*.png"))
    new_files = after_files - before_files
    assert len(new_files) == 1
    test_file = list(new_files)[0]
    assert test_file.exists()

    # 3. Delete session via API
    del_resp = client.delete(f"/sessions/{session_id}")
    assert del_resp.status_code == 204

    # 4. Verify physical file was purged from disk
    assert not test_file.exists(), "Physical file should have been removed upon session deletion!"

def test_log_sanitization_filter():
    """Verify that sensitive secrets and tokens are redacted from log records."""
    filter_instance = SanitizingFilter()

    # Test Google Gemini API Key masking (constructed dynamically to avoid false-positive scanner alerts)
    dummy_key_prefix = "AI" + "za"
    dummy_key = dummy_key_prefix + ("0" * 35)
    record1 = logging.LogRecord("test", logging.INFO, "", 0, f"Connected with key {dummy_key}", (), None)
    filter_instance.filter(record1)
    assert dummy_key_prefix not in record1.msg
    assert "[REDACTED_API_KEY]" in record1.msg

    # Test Database URL password masking
    record2 = logging.LogRecord("test", logging.INFO, "", 0, "DB url: mysql+pymysql://root:supersecretpassword@localhost:3306/db", (), None)
    filter_instance.filter(record2)
    assert "supersecretpassword" not in record2.msg
    assert "[REDACTED_PASSWORD]" in record2.msg

def test_maintenance_endpoints():
    """Verify /maintenance/storage and /maintenance/cleanup endpoints."""
    # Storage stats
    stats_resp = client.get("/maintenance/storage")
    assert stats_resp.status_code == 200
    data = stats_resp.json()
    assert "uploads_count" in data
    assert "audio_cache_count" in data

    # Trigger cleanup
    cleanup_resp = client.post("/maintenance/cleanup", json={"max_age_hours": 48})
    assert cleanup_resp.status_code == 200
    assert "files_purged" in cleanup_resp.json()
