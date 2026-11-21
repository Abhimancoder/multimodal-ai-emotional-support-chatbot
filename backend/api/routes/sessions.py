from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.schemas.session import SessionItem, MessageItem, SessionDetail
from backend.services.chat_service import ChatService

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("", response_model=List[SessionItem])
async def list_chat_sessions(db: Session = Depends(get_db)) -> List[SessionItem]:
    """Retrieves all active conversation sessions."""
    sessions = ChatService.list_sessions(db)
    return [
        SessionItem(
            id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            is_active=s.is_active
        )
        for s in sessions
    ]

@router.get("/{session_id}/messages", response_model=List[MessageItem])
async def get_session_messages(
    session_id: str,
    db: Session = Depends(get_db)
) -> List[MessageItem]:
    """Retrieves all messages for a specific session."""
    messages = ChatService.get_session_messages(db, session_id)
    return [
        MessageItem(
            id=m.id,
            role=m.role.value if hasattr(m.role, "value") else str(m.role),
            content=m.content,
            modality=m.modality.value if hasattr(m.modality, "value") else str(m.modality),
            tts_audio_path=m.tts_audio_path,
            has_grounding_card=m.has_grounding_card,
            card_type=m.card_type,
            created_at=m.created_at
        )
        for m in messages
    ]

@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Deletes a conversation session and all its messages."""
    success = ChatService.delete_session(db, session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found."
        )
    return None
