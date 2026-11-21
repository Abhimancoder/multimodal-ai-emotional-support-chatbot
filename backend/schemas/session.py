from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class MessageItem(BaseModel):
    """Schema for a single message turn in the history."""
    id: int
    role: str
    content: str
    modality: str
    tts_audio_path: Optional[str] = None
    has_grounding_card: bool = False
    card_type: Optional[str] = None
    created_at: datetime

class SessionItem(BaseModel):
    """Schema for session list preview."""
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

class SessionDetail(BaseModel):
    """Schema for complete session with all messages."""
    id: str
    title: str
    created_at: datetime
    messages: List[MessageItem]
