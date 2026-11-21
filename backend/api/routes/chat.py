from typing import Optional, List, Dict, Any
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.core.config import settings
from backend.core.logging import logger
from backend.database.connection import get_db
from backend.database.models import ModalityEnum, SafetyTriggerEnum, SafetyActionEnum, SafetyEvent
from backend.schemas.chat import ChatResponse
from backend.services.chat_service import ChatService
from backend.services.safety.classifier import SafetyClassifier
from backend.services.safety.file_validator import FileValidator
from backend.services.safety.output_guard import OutputGuard
from backend.services.audio.stt_service import stt_service
from backend.services.audio.tts_service import tts_service
from backend.services.rag.retriever import rag_retriever
from backend.services.emotional_support.persona import EMOTIONAL_SUPPORT_SYSTEM_PROMPT
from backend.services.emotional_support.grounding import GroundingService
from backend.services.ai.gemini_provider import ai_provider

router = APIRouter(prefix="/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse)
async def send_chat_message(
    request: Request,
    db: Session = Depends(get_db)
) -> ChatResponse:
    """
    Unified multimodal conversation endpoint with multi-category safety guardrails.
    """
    content_type = request.headers.get("content-type", "")

    user_text: Optional[str] = None
    session_id: Optional[str] = None
    image_file: Optional[UploadFile] = None
    audio_file: Optional[UploadFile] = None
    enable_audio: bool = False

    if "application/json" in content_type:
        try:
            body = await request.json()
            user_text = body.get("message", "").strip()
            session_id = body.get("session_id")
            enable_audio = bool(body.get("enable_audio", False))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload."
            )
    else:
        # Multipart / Form Data
        form = await request.form()
        raw_msg = form.get("message")
        user_text = raw_msg.strip() if isinstance(raw_msg, str) and raw_msg.strip() else None
        raw_sess = form.get("session_id")
        session_id = raw_sess if isinstance(raw_sess, str) and raw_sess.strip() else None
        
        # Audio generation preference
        raw_aud_pref = form.get("enable_audio")
        if isinstance(raw_aud_pref, str) and raw_aud_pref.lower() in ["true", "1", "yes"]:
            enable_audio = True

        raw_img = form.get("image")
        if hasattr(raw_img, "filename") and raw_img.filename:
            image_file = raw_img
            
        raw_aud = form.get("audio")
        if hasattr(raw_aud, "filename") and raw_aud.filename:
            audio_file = raw_aud

    # Validate that at least one modality is present
    if not user_text and not image_file and not audio_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content cannot be empty. Please provide text, an image, or an audio file."
        )

    # 1. Session Management
    session = ChatService.get_or_create_session(db, session_id)

    # 2. File Validation and Storage
    image_bytes: Optional[bytes] = None
    image_mime: Optional[str] = None
    audio_transcript: Optional[str] = None
    media_records: List[Dict[str, Any]] = []

    # Process Image
    if image_file:
        img_content, img_mime, img_savename = await FileValidator.validate_image(image_file)
        img_dest = settings.uploads_dir / img_savename
        FileValidator.save_file_to_disk(img_content, img_dest)
        image_bytes = img_content
        image_mime = img_mime
        media_records.append({
            "original_filename": image_file.filename or "image.png",
            "storage_path": str(img_dest),
            "mime_type": img_mime,
            "file_size_bytes": len(img_content)
        })

    # Process Audio
    if audio_file:
        aud_content, aud_mime, aud_savename = await FileValidator.validate_audio(audio_file)
        aud_dest = settings.uploads_dir / aud_savename
        FileValidator.save_file_to_disk(aud_content, aud_dest)
        media_records.append({
            "original_filename": audio_file.filename or "audio.wav",
            "storage_path": str(aud_dest),
            "mime_type": aud_mime,
            "file_size_bytes": len(aud_content)
        })
        audio_transcript = await stt_service.transcribe_audio(aud_dest, aud_mime)

    # Determine Modality Enum
    modality_count = sum(1 for m in [user_text, image_bytes, audio_file] if m is not None)
    if modality_count > 1:
        modality = ModalityEnum.MULTIMODAL
    elif image_bytes is not None:
        modality = ModalityEnum.IMAGE
    elif audio_file is not None:
        modality = ModalityEnum.AUDIO
    else:
        modality = ModalityEnum.TEXT

    # 3. Construct Unified Text for Safety & Prompting
    text_to_evaluate = []
    if user_text:
        text_to_evaluate.append(user_text)
    if audio_transcript:
        text_to_evaluate.append(audio_transcript)
    combined_text = " ".join(text_to_evaluate).strip()

    # 4. Multi-Category Safety Guardrail Checks
    # Category A: Acute Crisis / Self-Harm
    is_crisis, _ = SafetyClassifier.detect_crisis(combined_text)
    if is_crisis:
        assistant_reply = SafetyClassifier.get_crisis_intervention_message()
        user_msg, assistant_msg = ChatService.save_turn(
            db=db,
            session_id=session.id,
            user_text=combined_text or "[Image Shared]",
            assistant_text=assistant_reply,
            modality=modality,
            media_records=media_records,
            is_crisis=True
        )
        return ChatResponse(
            session_id=session.id,
            user_message=combined_text or "[Image Shared]",
            assistant_message=assistant_reply,
            modality=modality.value,
            audio_transcript=audio_transcript,
            has_image=bool(image_bytes),
            is_crisis=True,
            safety_trigger="crisis_self_harm",
            created_at=assistant_msg.created_at
        )

    # Category B: Medical / Psychiatric Diagnosis Request
    is_medical, _ = SafetyClassifier.detect_medical_request(combined_text)
    if is_medical:
        assistant_reply = SafetyClassifier.get_medical_deflection_message()
        user_msg, assistant_msg = ChatService.save_turn(
            db=db,
            session_id=session.id,
            user_text=combined_text,
            assistant_text=assistant_reply,
            modality=modality,
            media_records=media_records,
            is_crisis=False
        )
        # Log safety audit event
        safety_log = SafetyEvent(
            session_id=session.id,
            trigger_type=SafetyTriggerEnum.MEDICAL_ADVICE_REQUEST,
            action_taken=SafetyActionEnum.DISCLAIMER_APPENDED
        )
        db.add(safety_log)
        db.commit()

        return ChatResponse(
            session_id=session.id,
            user_message=combined_text,
            assistant_message=assistant_reply,
            modality=modality.value,
            audio_transcript=audio_transcript,
            has_image=bool(image_bytes),
            is_crisis=False,
            safety_trigger="medical_advice_request",
            created_at=assistant_msg.created_at
        )

    # Category C: Adversarial Prompt Injection / Jailbreak
    is_injection, _ = SafetyClassifier.detect_prompt_injection(combined_text)
    if is_injection:
        assistant_reply = SafetyClassifier.get_injection_deflection_message()
        user_msg, assistant_msg = ChatService.save_turn(
            db=db,
            session_id=session.id,
            user_text=combined_text,
            assistant_text=assistant_reply,
            modality=modality,
            media_records=media_records,
            is_crisis=False
        )
        safety_log = SafetyEvent(
            session_id=session.id,
            trigger_type=SafetyTriggerEnum.PROMPT_INJECTION,
            action_taken=SafetyActionEnum.BLOCKED
        )
        db.add(safety_log)
        db.commit()

        return ChatResponse(
            session_id=session.id,
            user_message=combined_text,
            assistant_message=assistant_reply,
            modality=modality.value,
            audio_transcript=audio_transcript,
            has_image=bool(image_bytes),
            is_crisis=False,
            safety_trigger="prompt_injection",
            created_at=assistant_msg.created_at
        )

    # 5. Fetch prior session context
    history = ChatService.get_recent_history(db, session_id=session.id, limit=6)

    # 6. RAG Retrieval: Query knowledge base for relevant literature
    rag_context, citations = rag_retriever.retrieve_context(
        query_text=combined_text or (user_text or ""),
        top_k=2
    )

    # 7. Check for structured grounding exercise opportunity
    card_type = GroundingService.detect_grounding_opportunity(combined_text)
    grounding_card = GroundingService.get_exercise_details(card_type) if card_type else None

    # 8. Generate Multimodal Response from AI Provider
    assistant_reply = await ai_provider.generate_multimodal_response(
        prompt=user_text,
        image_bytes=image_bytes,
        image_mime=image_mime,
        audio_transcript=audio_transcript,
        history=history,
        system_instruction=EMOTIONAL_SUPPORT_SYSTEM_PROMPT,
        rag_context=rag_context
    )

    # 9. Output Guard: Sanitize AI output to prevent clinical diagnosis slips
    sanitized_reply, _ = OutputGuard.inspect_and_sanitize(assistant_reply)

    # 10. Optional Text-to-Speech (TTS) Synthesis
    tts_audio_url: Optional[str] = None
    tts_audio_path: Optional[str] = None
    if enable_audio:
        try:
            aud_path, _, aud_name = await tts_service.synthesize_speech(sanitized_reply)
            tts_audio_url = f"/audio/{aud_name}"
            tts_audio_path = str(aud_path)
        except Exception as exc:
            logger.error(f"Failed to generate TTS audio: {exc}")

    # 11. Persist turns & media metadata
    user_record_text = user_text or (f"[Voice Note]: {audio_transcript}" if audio_transcript else "[Shared an Image]")
    user_msg, assistant_msg = ChatService.save_turn(
        db=db,
        session_id=session.id,
        user_text=user_record_text,
        assistant_text=sanitized_reply,
        modality=modality,
        media_records=media_records,
        is_crisis=False
    )

    if card_type:
        assistant_msg.has_grounding_card = True
        assistant_msg.card_type = card_type

    if tts_audio_path:
        assistant_msg.tts_audio_path = tts_audio_path

    db.commit()

    return ChatResponse(
        session_id=session.id,
        user_message=user_record_text,
        assistant_message=sanitized_reply,
        modality=modality.value,
        audio_transcript=audio_transcript,
        has_image=bool(image_bytes),
        is_crisis=False,
        audio_url=tts_audio_url,
        grounding_card=grounding_card,
        citations=citations,
        created_at=assistant_msg.created_at
    )
