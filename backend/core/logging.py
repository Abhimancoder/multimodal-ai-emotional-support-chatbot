import logging
import re
import sys
from backend.core.config import settings

class SanitizingFilter(logging.Filter):
    """
    Filters sensitive secrets, API keys, and credentials from log messages
    before they are printed to console or written to disk.
    """
    SENSITIVE_PATTERNS = [
        (re.compile(r"AIza[0-9A-Za-z-_]{35}"), "[REDACTED_API_KEY]"),
        (re.compile(r"(?i)(password|secret|token)\s*=\s*['\"]?[^\s'\"]+"), r"\1=[REDACTED]"),
        (re.compile(r"Bearer\s+[A-Za-z0-9\-_\.]+"), "Bearer [REDACTED_TOKEN]"),
        (re.compile(r"://([^:]+):([^@]+)@"), r"://\1:[REDACTED_PASSWORD]@")
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                record.msg = pattern.sub(replacement, record.msg)
        return True

def setup_logger(name: str = "emotional_support_api") -> logging.Logger:
    """Configures a sanitized application logger."""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.addFilter(SanitizingFilter())
        logger.addHandler(console_handler)
        
    return logger

logger = setup_logger()
