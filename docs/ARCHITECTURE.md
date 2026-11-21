# System Architecture & Component Design

## 1. Architectural Layers

### A. Presentation Layer (Streamlit)
- Path: `frontend/`
- Runs as an independent process on port `8501`.
- Communicates with FastAPI via HTTP JSON and multipart form data.
- Handles UI rendering: chat history, file pickers, audio recording, audio playback, and visual grounding cards.

### B. Gateway & API Layer (FastAPI)
- Path: `backend/`
- Runs as an async ASGI server (Uvicorn) on port `8000`.
- Routes:
  - `POST /chat`: Unified multimodal conversation endpoint.
  - `GET /health`: System, database, and model provider health check.
  - `GET /sessions`: Conversation session management.
  - `POST /rag/ingest`: Knowledge base document indexing.

### C. Service Layer
- **AI Service (`backend/services/ai/`):** Implements `BaseAIProvider` interface. Integrates multimodal models (Gemini 1.5).
- **Safety Service (`backend/services/safety/`):** Evaluates prompts for self-harm/crisis, validates file types by magic bytes, sanitizes outputs.
- **RAG Service (`backend/services/rag/`):** Chunking, embedding generation, ChromaDB vector retrieval, and citation building.
- **Audio Service (`backend/services/audio/`):** Speech-to-Text (STT) and Text-to-Speech (TTS).

### D. Data Persistence Layer
- **Relational DB (MySQL):** Stores sessions, messages, media paths, and safety audit logs.
- **Vector DB (ChromaDB):** Stores high-dimensional embeddings for psychoeducation documents.
- **Local Storage (`storage/`):** Stores temporary uploads and generated audio files with randomized UUID filenames.
