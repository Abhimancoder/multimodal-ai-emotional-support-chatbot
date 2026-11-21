import uuid
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.database.models import (
    ChatSession,
    Message,
    RoleEnum,
    ModalityEnum,
    SafetyEvent,
    SafetyTriggerEnum,
    SafetyActionEnum
)
from backend.core.logging import logger

class ChatService:
    """Manages chat sessions, messages, and conversation persistence."""

    @staticmethod
    def get_or_create_session(db: Session, session_id: Optional[str] = None) -> ChatSession:
        """Retrieves an existing session by ID or creates a new one with a unique UUID."""
        if session_id:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                return session

        # Generate a new session UUID
        new_id = str(uuid.uuid4())
        session = ChatSession(
            id=new_id,
            title="New Conversation",
            is_active=True
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"Created new chat session: {new_id}")
        return session

    @staticmethod
    def get_recent_history(db: Session, session_id: str, limit: int = 6) -> List[Dict[str, str]]:
        """
        Retrieves recent turns from the database formatted for LLM context.
        Returns a list of dicts: [{'role': 'user'|'assistant', 'content': '...'}]
        """
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        messages.reverse()

        history = []
        for msg in messages:
            history.append({
                "role": msg.role.value if hasattr(msg.role, "value") else str(msg.role),
                "content": msg.content
            })
        return history

    @staticmethod
    def save_turn(
        db: Session,
        session_id: str,
        user_text: str,
        assistant_text: str,
        modality: ModalityEnum = ModalityEnum.TEXT,
        media_records: Optional[List[Dict[str, Any]]] = None,
        is_crisis: bool = False
    ) -> Tuple[Message, Message]:
        """Persists the user message and assistant message turns atomically, including media metadata."""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if session and session.title == "New Conversation":
            summary = user_text.strip().replace("\n", " ")[:35]
            session.title = summary if summary else f"Conversation ({modality.value.title()})"

        now = datetime.now(timezone.utc)

        # 1. User Message
        user_msg = Message(
            session_id=session_id,
            role=RoleEnum.USER,
            content=user_text,
            modality=modality,
            created_at=now
        )
        db.add(user_msg)
        db.flush()  # Flush to populate user_msg.id for foreign keys

        # Attach media records if present
        if media_records:
            from backend.database.models import MediaMetadata
            for med in media_records:
                meta = MediaMetadata(
                    message_id=user_msg.id,
                    original_filename=med["original_filename"],
                    storage_path=med["storage_path"],
                    mime_type=med["mime_type"],
                    file_size_bytes=med["file_size_bytes"],
                    created_at=now
                )
                db.add(meta)

        # 2. Assistant Message
        assistant_msg = Message(
            session_id=session_id,
            role=RoleEnum.ASSISTANT,
            content=assistant_text,
            modality=modality,
            created_at=now
        )
        db.add(assistant_msg)

        # 3. Log Safety Event if crisis occurred
        if is_crisis:
            safety_log = SafetyEvent(
                session_id=session_id,
                trigger_type=SafetyTriggerEnum.CRISIS_SELF_HARM,
                action_taken=SafetyActionEnum.CRISIS_HELPLINE_INJECTED,
                timestamp=now
            )
            db.add(safety_log)

        db.commit()
        db.refresh(user_msg)
        db.refresh(assistant_msg)
        return user_msg, assistant_msg

    @staticmethod
    def list_sessions(db: Session, limit: int = 20) -> List[ChatSession]:
        """Lists active chat sessions ordered by most recently updated."""
        return (
            db.query(ChatSession)
            .filter(ChatSession.is_active == True)
            .order_by(ChatSession.updated_at.desc())
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_session_messages(db: Session, session_id: str) -> List[Message]:
        """Returns all messages for a given session in chronological order."""
        return (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
            .all()
        )

    @staticmethod
    def delete_session(db: Session, session_id: str) -> bool:
        """Deletes a session, cascades deletes to DB messages, and purges physical files from disk."""
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return False

        # First purge all physical image and audio files from storage disk
        from backend.services.safety.cleanup_service import cleanup_service
        purged_files = cleanup_service.purge_session_media(db, session_id)
        logger.info(f"Purged {purged_files} physical media files for session {session_id}")

        # Delete database session (foreign keys cascade to messages and media_metadata)
        db.delete(session)
        db.commit()
        logger.info(f"Deleted chat session from database: {session_id}")
        return True
