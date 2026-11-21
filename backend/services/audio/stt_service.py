from typing import Optional
from pathlib import Path
import google.generativeai as genai
from backend.core.config import settings
from backend.core.logging import logger

class STTService:
    """
    Speech-to-Text Service.
    Transcribes audio files into text for conversational understanding.
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self._is_configured = bool(self.api_key and not self.api_key.startswith("your_"))

    async def transcribe_audio(self, audio_path: Path, mime_type: str) -> str:
        """
        Transcribes the given audio file at audio_path.
        Returns the transcribed text string.
        """
        if not audio_path.exists():
            logger.error(f"Audio file not found at: {audio_path}")
            return "[Audio file not found]"

        if not self._is_configured:
            # Deterministic mock transcript for local offline testing
            logger.info("STT running in development mock mode.")
            return "I am feeling a little overwhelmed and need some calming thoughts."

        try:
            logger.info(f"Transcribing audio file ({mime_type}) using Gemini...")
            audio_file = genai.upload_file(path=str(audio_path), mime_type=mime_type)
            
            model = genai.GenerativeModel(model_name=settings.GEMINI_MODEL)
            prompt = "Please provide an exact, faithful transcription of this audio clip. Do not summarize or add commentary."
            response = model.generate_content([audio_file, prompt])
            
            transcript = response.text.strip()
            logger.info(f"Audio transcribed successfully ({len(transcript)} chars).")
            return transcript

        except Exception as exc:
            logger.error(f"Failed to transcribe audio: {exc}")
            return "[Audio transcription encountered a temporary error]"

stt_service = STTService()
