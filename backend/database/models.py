import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Boolean,
    Float,
    Enum
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class RoleEnum(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ModalityEnum(str, enum.Enum):
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MULTIMODAL = "multimodal"

class SafetyTriggerEnum(str, enum.Enum):
    CRISIS_SELF_HARM = "crisis_self_harm"
    MEDICAL_ADVICE_REQUEST = "medical_advice_request"
    PROMPT_INJECTION = "prompt_injection"
    MALFORMED_FILE = "malformed_file"

class SafetyActionEnum(str, enum.Enum):
    CRISIS_HELPLINE_INJECTED = "crisis_helpline_injected"
    DISCLAIMER_APPENDED = "disclaimer_appended"
    BLOCKED = "blocked"

class ChatSession(Base):
    """Represents a conversational session thread."""
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True)  # UUID v4
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=get_utc_now, nullable=False)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    safety_events = relationship("SafetyEvent", back_populates="session")

class Message(Base):
    """Represents an individual turn in a conversation."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(Enum(RoleEnum), nullable=False)
    content = Column(Text, nullable=False)
    modality = Column(Enum(ModalityEnum), default=ModalityEnum.TEXT, nullable=False)
    tts_audio_path = Column(String(512), nullable=True)
    has_grounding_card = Column(Boolean, default=False, nullable=False)
    card_type = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    media = relationship("MediaMetadata", back_populates="message", cascade="all, delete-orphan")

class MediaMetadata(Base):
    """Metadata for uploaded images or audio clips."""
    __tablename__ = "media_metadata"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(512), nullable=False)
    mime_type = Column(String(64), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    duration_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime, default=get_utc_now, nullable=False)

    # Relationships
    message = relationship("Message", back_populates="media")

class KnowledgeDocument(Base):
    """Tracks documents ingested into the RAG vector index."""
    __tablename__ = "knowledge_documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_title = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False)
    file_path = Column(String(512), nullable=False)
    total_chunks = Column(Integer, default=0, nullable=False)
    indexed_at = Column(DateTime, default=get_utc_now, nullable=False)

class SafetyEvent(Base):
    """Audit log for safety incidents and crisis interventions."""
    __tablename__ = "safety_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True)
    trigger_type = Column(Enum(SafetyTriggerEnum), nullable=False)
    action_taken = Column(Enum(SafetyActionEnum), nullable=False)
    timestamp = Column(DateTime, default=get_utc_now, nullable=False)

    # Relationships
    session = relationship("ChatSession", back_populates="safety_events")
