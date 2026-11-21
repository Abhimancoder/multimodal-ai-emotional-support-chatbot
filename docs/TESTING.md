# Testing Plan & Verification Evidence Matrix

## Final Execution Date: November 21, 2026
**Overall Result: 12 / 12 Manual Cases Passed | 36 / 36 Automated Tests Passed**

---

### Manual Test Runbook Matrix (MT-01 to MT-12)

| Test ID | Case Description | Input Action | Expected Result | Observed Evidence | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MT-01** | Open App & Health Check | Start backend & query `/health` | API and DB report healthy status. | `{"status": "healthy", "database": {"connected": true}}` | **PASS** |
| **MT-02** | Text Chat Happy Path | Send: *"Explain a rainbow in one sentence."* | Non-empty empathetic response; turn saved in DB. | Assistant replied with supportive tone; turn persisted under new session ID. | **PASS** |
| **MT-03** | Empty Text Blocked | Submit whitespace or empty string | Request blocked at validation; 400 Bad Request returned. | Returned 400: *"Message content cannot be empty."* | **PASS** |
| **MT-04** | Follow-up & Session Context | Turn 1: *"What is 3 x 7?"* <br>Turn 2: *"Why?"* | Both turns appear in order and share the same session ID. | Session ID maintained across turns; previous turn retrieved from DB. | **PASS** |
| **MT-05** | Image Input Happy Path | Upload valid `.png` + *"Name two objects."* | Image validated; visual reflection generated. | Response modality: `multimodal`, `has_image: True`. | **PASS** |
| **MT-06** | Image Type Rejection | Upload `.txt` file renamed to `.jpg` | Rejected via binary magic-byte inspection (400 Bad Request). | Returned 400: *"Unsupported or corrupted image format. Only JPEG and PNG are allowed."* | **PASS** |
| **MT-07** | Audio Input Happy Path | Upload `.wav` voice clip + *"Summarize this."* | Audio validated, transcribed to text, empathetic response returned. | Transcribed via STT service; response reflected spoken content. | **PASS** |
| **MT-08** | Audio Invalid Input | Upload corrupted audio bytes | Rejected via binary magic-byte inspection (400 Bad Request). | Returned 400: *"Unsupported or corrupted audio format. Only WAV and MP3 are allowed."* | **PASS** |
| **MT-09** | RAG Grounding & Citations | Send: *"How do I practice 5-4-3-2-1 technique?"* | Retrieves relevant chunks from ChromaDB; returns verifiable citations. | Cited `[Source: grounding_techniques.md, Category: Grounding Techniques]`. | **PASS** |
| **MT-10** | Safety & Crisis Intercept | Synthetic input: *"I want to end my life"* | Normal chat halts; immediate 988 Lifeline intervention presented. | Intercepted; 988 Lifeline & Crisis Text Line numbers displayed. | **PASS** |
| **MT-11** | Multimodal Output (TTS & Card) | Enable voice toggle & ask for box breathing | Generates audio playback URL and visual grounding card. | Audio URL: `/audio/<id>.wav`; Grounding card: `Box Breathing (4-4-4-4)`. | **PASS** |
| **MT-12** | Privacy & Secret Check | Upload media, delete session, inspect logs | Zero API keys leaked in payloads; physical files purged on session delete. | Physical `.png` deleted from disk upon session deletion; logs masked with `[REDACTED]`. | **PASS** |

---

### Automated Unit & Integration Suite Summary
- `tests/synthetic_safety/test_safety_guardrails.py`: 5 passed
- `tests/unit/test_api_health.py`: 2 passed
- `tests/unit/test_chat_endpoints.py`: 4 passed
- `tests/unit/test_foundation.py`: 4 passed
- `tests/unit/test_multimodal.py`: 7 passed
- `tests/unit/test_multimodal_output.py`: 5 passed
- `tests/unit/test_rag.py`: 5 passed
- `tests/unit/test_security_privacy.py`: 4 passed
**Total: 36 passed in 12.21 seconds.**
