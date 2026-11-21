# Phase-Wise Implementation Plan

## Phase 0: Discovery & Specification (Completed)
- Inspect environment, establish specifications and design documents.

## Phase 1: Foundation Setup (Current Phase)
- Environment setup, configuration manager (`pydantic-settings`).
- FastAPI server setup with `/health` endpoint and CORS middleware.
- Database engine with MySQL support and local SQLite fallback.
- Streamlit application skeleton with API health monitoring and disclaimer banner.

## Phase 2: Core Text Chat
- Implement `POST /chat` for text messages.
- AI provider integration (Google Gemini 1.5).
- Session tracking and MySQL message persistence.
- Streamlit conversational chat interface.

## Phase 3: Multimodal Input (Image & Audio)
- File validation service (magic bytes, size limits).
- Image upload and multimodal LLM processing.
- Audio upload and Speech-to-Text (STT) transcription.
- Multi-input fusion (Text + Image + Audio).

## Phase 4: RAG Engine
- Knowledge base document loader (Markdown, TXT, PDF).
- Chunking and local ChromaDB vector indexing.
- Semantic retrieval and context augmentation with citations.

## Phase 5: Emotional Support & Safety Engine
- Empathetic prompt engineering & cognitive reframing.
- Crisis detection classifier and 988 lifeline intervention.
- Non-clinical boundary enforcement.

## Phase 6: Multimodal Output
- Text-to-Speech (TTS) engine integration.
- Streamlit audio player for assistant replies.
- Interactive grounding UI cards (e.g., box breathing visual guide).

## Phase 7: Security & Privacy Hardening
- Complete upload security review, temporary file cleanup, log sanitization.

## Phase 8: Final Integration & Verification
- Execute 12-point manual test matrix (MT-01 to MT-12).
- Final walkthrough, README and lab evidence documentation.
