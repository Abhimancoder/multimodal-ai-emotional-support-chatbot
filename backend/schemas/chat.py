from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Schema for text-only JSON chat requests (backward compatibility)."""
    session_id: Optional[str] = Field(
        default=None,
        description="Session UUID. If omitted, a new conversation session is created."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User text input prompt"
    )
    enable_audio: bool = Field(
        default=False,
        description="Whether to synthesize speech output (TTS)"
    )

class CitationItem(BaseModel):
    source: str
    category: str

class ChatResponse(BaseModel):
    """Schema for assistant chat response."""
    session_id: str
    user_message: str
    assistant_message: str
    modality: str = "text"
    audio_transcript: Optional[str] = None
    has_image: bool = False
    is_crisis: bool = False
    safety_trigger: Optional[str] = None
    audio_url: Optional[str] = None
    grounding_card: Optional[Dict[str, Any]] = None
    citations: List[CitationItem] = []
    created_at: datetime
