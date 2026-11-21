# Project Specification: Multimodal AI Emotional Support Chatbot (RAG)

## 1. Project Overview
A multimodal AI emotional support companion built using Python, FastAPI, Streamlit, MySQL, and ChromaDB.
It accepts text, images, and audio, processes them in a unified conversational context, and delivers grounded, empathetic responses with strict safety guardrails.

## 2. Target Audience & Non-Clinical Boundary
- **Audience:** Students and general users seeking supportive, non-judgmental reflective listening and verified coping strategies.
- **Strict Boundary:** The application is an AI assistant, NOT a medical device, licensed therapist, or doctor. It never diagnoses conditions, prescribes medications, or provides clinical treatment.

## 3. Technology Stack
- **Frontend UI:** Streamlit (Python-based interactive web frontend)
- **Backend API:** FastAPI (Async Python REST API)
- **Relational DB:** MySQL (Conversation sessions, messages, media metadata, safety events) with fallback to SQLite for local development.
- **Vector DB:** ChromaDB (Semantic search over coping and mindfulness literature)
- **AI Engine:** Modular Multimodal LLM provider (Google Gemini 1.5 Flash / Pro)
- **Speech Services:** STT (Speech-to-Text) and TTS (Text-to-Speech)

## 4. Input & Output Modalities
- **Inputs:** Text (up to 2000 chars), Image (JPEG/PNG up to 5MB), Audio (WAV/MP3 up to 10MB).
- **Outputs:** Empathetic text response, optional TTS audio playback, structured visual grounding cards.

## 5. Acceptance Test Criteria
1. Text messages are submitted and answered empathetically.
2. Images are validated for MIME type, file size, and visual content.
3. Audio is transcribed to text accurately.
4. Multimodal combination (Text + Image + Audio) works in a single unified message.
5. RAG queries retrieve verified wellness information with citations.
6. Crisis keywords (e.g., self-harm, suicide) immediately trigger the 988 lifeline intervention response.
7. Secrets and API keys are strictly kept server-side in `.env`.
