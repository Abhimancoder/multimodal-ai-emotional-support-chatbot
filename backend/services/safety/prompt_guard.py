import re
from typing import Tuple, Optional
from backend.core.logging import logger

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"system\s+prompt\s+(reveal|leak|show|display|print)",
    r"reveal\s+(your|the)\s+(system\s+prompt|internal\s+instructions|api\s*key)",
    r"bypass\s+(all\s+)?(safety|guardrails|filters|content\s+policies)",
    r"do\s+anything\s+now|dan\s+mode|jailbreak",
    r"you\s+are\s+now\s+(unfiltered|unrestricted|evil|an\s+unconstrained\s+ai)",
    r"pretend\s+you\s+have\s+no\s+(rules|restrictions|ethics|safety)"
]

class PromptGuard:
    """Detects and deflects prompt injection, system leakage, and jailbreak attempts."""

    @staticmethod
    def detect_injection(text: str) -> Tuple[bool, Optional[str]]:
        """
        Inspects input text for adversarial prompt injection patterns.
        Returns: (is_injection: bool, matched_pattern: Optional[str])
        """
        if not text:
            return False, None

        normalized = text.lower()
        for pattern in INJECTION_PATTERNS:
            match = re.search(pattern, normalized)
            if match:
                logger.warning(f"Prompt injection pattern detected: '{match.group(0)}'")
                return True, match.group(0)

        return False, None

    @staticmethod
    def get_injection_deflection_message() -> str:
        """Returns standard response when a prompt injection attempt is deflected."""
        return (
            "I am designed to be an empathetic emotional support companion focused on well-being and grounding. "
            "I cannot alter my core instructions, bypass safety guidelines, or share internal configurations. "
            "How can I support your personal well-being today?"
        )
