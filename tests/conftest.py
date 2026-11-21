import pytest
from backend.services.ai.gemini_provider import ai_provider
from backend.services.audio.stt_service import stt_service

@pytest.fixture(autouse=True)
def mock_external_ai_services_for_testing():
    """
    Autouse fixture that ensures automated unit tests run deterministically
    in offline development/mock mode without calling outbound Google APIs
    or consuming API quota.
    """
    orig_ai = ai_provider._is_configured
    orig_stt = stt_service._is_configured

    ai_provider._is_configured = False
    stt_service._is_configured = False

    yield

    ai_provider._is_configured = orig_ai
    stt_service._is_configured = orig_stt
