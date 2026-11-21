import pytest
from backend.core.config import settings
from backend.services.safety.classifier import SafetyClassifier

def test_settings_load():
    """Verify that configuration settings load with sensible defaults."""
    assert settings.ENVIRONMENT in ["development", "production", "testing"]
    assert settings.BACKEND_PORT == 8000
    assert settings.FRONTEND_PORT == 8501
    assert settings.MAX_IMAGE_SIZE_BYTES > 0
    assert settings.MAX_AUDIO_SIZE_BYTES > 0

def test_safety_classifier_empty_input():
    """Verify that empty and whitespace-only text is rejected."""
    assert SafetyClassifier.is_empty_or_whitespace("") is True
    assert SafetyClassifier.is_empty_or_whitespace("   ") is True
    assert SafetyClassifier.is_empty_or_whitespace("\n\t") is True
    assert SafetyClassifier.is_empty_or_whitespace("Hello") is False

def test_safety_classifier_crisis_detection():
    """Verify that acute distress/crisis keywords are caught."""
    # Synthetic test phrases
    is_crisis, reason = SafetyClassifier.detect_crisis("I feel like I want to die")
    assert is_crisis is True
    assert reason == "crisis_self_harm"

    is_crisis, reason = SafetyClassifier.detect_crisis("I want to commit suicide")
    assert is_crisis is True

    # Safe test phrases
    is_crisis, reason = SafetyClassifier.detect_crisis("I am feeling stressed about my exam")
    assert is_crisis is False
    assert reason is None

def test_crisis_intervention_message():
    """Verify that the crisis intervention message includes official 988 lifeline."""
    msg = SafetyClassifier.get_crisis_intervention_message()
    assert "988" in msg
    assert "Crisis Text Line" in msg
