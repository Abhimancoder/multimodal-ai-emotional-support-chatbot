# Mindful Companion: Multimodal AI Emotional Support Chatbot (RAG)

An empathetic, multimodal AI companion providing supportive reflective listening, grounding techniques, and verified psychoeducation using RAG, FastAPI, Streamlit, and MySQL.

---

## 🏗️ Architecture & Technology Stack
- **Frontend UI:** Streamlit (`frontend/app.py`)
- **Backend REST API:** FastAPI (`backend/main.py`)
- **Database:** MySQL on `localhost:3306` with automatic local SQLite fallback (`storage/app.db`)
- **Vector Database:** ChromaDB (`storage/chromadb/`) with 384-dimensional offline-safe cosine embeddings
- **Multimodal AI Provider:** Google Gemini 1.5 (`backend/services/ai/gemini_provider.py`)
- **Audio Services:** Speech-to-Text (STT) and Text-to-Speech (TTS) with offline chime fallback
- **Safety & Guardrails:** Multi-category crisis detection, prompt-injection defense, and non-clinical boundary filters

---

## 📁 Accepted Media Formats & Limits
- **Image Inputs:** PNG, JPEG (`.png`, `.jpg`, `.jpeg`) — Max size: **5 MB**. Validated via binary magic bytes.
- **Audio Inputs:** WAV, MP3 (`.wav`, `.mp3`) — Max size: **10 MB**. Validated via binary magic bytes.
- **Text Inputs:** Natural language up to 2,000 characters per turn.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- Python 3.12+ (tested on Python 3.12.10)
- Windows PowerShell, macOS, or Linux terminal

### 2. Environment Setup
Create a virtual environment and install dependencies:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configuration (`.env`)
The project comes pre-configured with a development `.env` file. To connect live Gemini API:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```
*(If no API key is set, the chatbot automatically runs in Development/Test Mode so you can test all features without an external key).*

### 4. Running the Application

**Terminal 1 — FastAPI Backend Server:**
```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir backend
```
- Interactive Swagger API docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

**Terminal 2 — Streamlit Frontend UI:**
```powershell
.\.venv\Scripts\Activate.ps1
streamlit run frontend/app.py
```
- Open your browser at `http://localhost:8501`.

---

## 🧪 Running Automated Tests
Run the entire 36-test automated verification suite:
```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Execute the 12-point manual test matrix script:
```powershell
.\.venv\Scripts\python.exe tests/run_verification_runbook.py
```
*(Result: 12 / 12 Manual Cases Passed | 36 / 36 Automated Tests Passed).*

---

## 🔒 Security & Privacy Notice
- **Server-Side Secrets:** API keys and credentials reside exclusively in `.env` and are never sent to the frontend.
- **Sanitized Logging:** All log output automatically redacts API keys and database passwords.
- **Right to Be Forgotten:** Deleting a conversation session permanently purges all uploaded images and generated audio files from the local storage disk.
- **Non-Clinical Boundary:** Mindful Companion is an AI companion for emotional reflection and grounding. It does not provide medical diagnoses or psychiatric treatment. In an acute emergency, dial **988** or local emergency services.
