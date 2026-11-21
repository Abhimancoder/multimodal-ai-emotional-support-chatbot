import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.audio.tts_service import tts_service
from backend.services.emotional_support.grounding import GroundingService

client = TestClient(app)

@pytest.mark.anyio
async def test_tts_service_generation():
    """Verify that TTS service generates a playable audio file."""
    text = "Take a slow, deep breath in and exhale gently."
    audio_path, mime_type, filename = await tts_service.synthesize_speech(text)
    assert audio_path.exists()
    assert audio_path.stat().st_size > 0
    assert mime_type in ["audio/mpeg", "audio/wav"]
    assert filename in str(audio_path)

def test_audio_serving_endpoint():
    """Verify GET /audio/{filename} serves files securely and blocks traversal."""
    # 1. Synthesize a test audio file
    import anyio
    audio_path, _, filename = anyio.run(tts_service.synthesize_speech, "Test audio playback")
    
    # 2. Fetch via API
    response = client.get(f"/audio/{filename}")
    assert response.status_code == 200
    assert response.headers["content-type"] in ["audio/mpeg", "audio/wav"]
    assert len(response.content) > 0

    # 3. Path traversal attack attempt
    traversal_response = client.get("/audio/../../storage/app.db")
    assert traversal_response.status_code == 404

    # 4. Non-existent file
    non_existent = client.get("/audio/non_existent_file_123.mp3")
    assert non_existent.status_code == 404

def test_chat_audio_preference_disabled():
    """Verify that when enable_audio is False, audio is NOT generated."""
    response = client.post(
        "/chat",
        json={"message": "Hello without audio", "enable_audio": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["audio_url"] is None

def test_chat_audio_preference_enabled():
    """Verify that when enable_audio is True, audio is synthesized and returned."""
    response = client.post(
        "/chat",
        json={"message": "Please speak your response to me", "enable_audio": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["audio_url"] is not None
    assert data["audio_url"].startswith("/audio/")

def test_grounding_card_structure():
    """Verify structured grounding card details and steps."""
    box_card = GroundingService.get_exercise_details("box_breathing")
    assert box_card is not None
    assert "Box Breathing" in box_card["title"]
    assert len(box_card["steps"]) == 4

    sensory_card = GroundingService.get_exercise_details("5_4_3_2_1")
    assert sensory_card is not None
    assert len(sensory_card["steps"]) == 5
