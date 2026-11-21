import re
from typing import Tuple
from backend.core.logging import logger

DIAGNOSIS_PATTERNS = [
    r"\bi\s+diagnose\s+you\s+with\b",
    r"\byou\s+(have|are\s+suffering\s+from)\s+(major\s+depressive\s+disorder|bipolar|schizophrenia|borderline)\b",
    r"\byou\s+should\s+take\s+(\d+\s*mg\s+of\s+)?(prozac|lexapro|zoloft|xanax|adderall|lithium|valium)\b"
]

class OutputGuard:
    """Post-generation safety filter for AI assistant output."""

    @staticmethod
    def inspect_and_sanitize(output_text: str) -> Tuple[str, bool]:
        """
        Validates model output to prevent accidental medical diagnoses or medication prescribing.
        Returns: (sanitized_text: str, violation_detected: bool)
        """
        if not output_text:
            return output_text, False

        normalized = output_text.lower()
        for pattern in DIAGNOSIS_PATTERNS:
            if re.search(pattern, normalized):
                logger.warning(f"Output guard triggered on clinical advice pattern: {pattern}")
                # Replace with grounded, non-clinical reminder
                sanitized = (
                    "I want to share supportive thoughts, but as an AI, I cannot provide medical or psychiatric diagnoses "
                    "or recommend specific prescription medications. If you are experiencing persistent distress, "
                    "speaking with a licensed physician, psychiatrist, or mental health counselor is the best and safest next step."
                )
                return sanitized, True

        return output_text, False
