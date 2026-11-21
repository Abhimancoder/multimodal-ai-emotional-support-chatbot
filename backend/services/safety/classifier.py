import re
from typing import Tuple, Optional
from backend.services.safety.crisis_resources import format_crisis_intervention_response
from backend.services.safety.prompt_guard import PromptGuard

CRISIS_PATTERNS = [
    r"\b(suicide|kill\s+myself|want\s+to\s+die|end\s+my\s+life|slit\s+my\s+wrist|hang\s+myself)\b",
    r"\b(hurt\s+myself|self\s*harm|take\s+all\s+my\s+pills|overdose|cut\s+myself)\b",
    r"\b(better\s+off\s+dead|no\s+reason\s+to\s+live|don'?t\s+want\s+to\s+wake\s+up)\b"
]

MEDICAL_DIAGNOSIS_REQUEST_PATTERNS = [
    r"\b(diagnose\s+me|give\s+me\s+a\s+diagnosis)\b",
    r"\bdo\s+i\s+have\s+(depression|adhd|bipolar|anxiety|schizophrenia|ptsd|ocd)\b",
    r"\bwhat\s+(mental\s+illness|disorder|condition)\s+do\s+i\s+have\b",
    r"\b(prescribe|recommend)\s+.*(meds|medication|pills|drugs)\b",
    r"\b(what|which)\s+(meds|medication|pills|drugs)\s+should\s+i\b"
]

class SafetyClassifier:
    """
    Evaluates input messages for safety violations:
    - Acute crisis / self-harm triggers
    - Medical/psychiatric diagnosis requests
    - Prompt injections and jailbreak attacks
    """

    @staticmethod
    def is_empty_or_whitespace(text: Optional[str]) -> bool:
        """Checks if text contains only whitespace or is empty."""
        return not text or len(text.strip()) == 0

    @staticmethod
    def detect_crisis(text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects acute crisis triggers requiring immediate intervention.
        Returns: (is_crisis: bool, matched_reason: Optional[str])
        """
        if not text:
            return False, None

        normalized = text.lower()
        for pattern in CRISIS_PATTERNS:
            if re.search(pattern, normalized):
                return True, "crisis_self_harm"

        return False, None

    @staticmethod
    def detect_medical_request(text: str) -> Tuple[bool, Optional[str]]:
        """
        Detects requests asking the AI to diagnose mental disorders or prescribe medication.
        """
        if not text:
            return False, None

        normalized = text.lower()
        for pattern in MEDICAL_DIAGNOSIS_REQUEST_PATTERNS:
            if re.search(pattern, normalized):
                return True, "medical_diagnosis_request"

        return False, None

    @staticmethod
    def detect_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
        """Delegates prompt injection checks to PromptGuard."""
        return PromptGuard.detect_injection(text)

    @staticmethod
    def get_crisis_intervention_message() -> str:
        """Returns standard verified compassionate crisis assistance message."""
        return format_crisis_intervention_response()

    @staticmethod
    def get_medical_deflection_message() -> str:
        """Returns non-clinical disclaimer deflection."""
        return (
            "I hear that you are reflecting on your mental well-being, but as an AI companion, "
            "I cannot diagnose medical or mental health conditions or suggest medications.\n\n"
            "If you are concerned about symptoms or feelings you are experiencing, I warmly encourage you "
            "to speak with a doctor, licensed clinical psychologist, or psychiatrist who can provide an accurate, "
            "personalized, and confidential clinical evaluation.\n\n"
            "In the meantime, I am happy to share general coping strategies, stress-relief practices, or simply listen."
        )

    @staticmethod
    def get_injection_deflection_message() -> str:
        """Returns response to adversarial prompts."""
        return PromptGuard.get_injection_deflection_message()
