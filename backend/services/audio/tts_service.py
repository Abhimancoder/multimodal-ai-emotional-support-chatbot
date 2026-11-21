import os
import uuid
import wave
import math
import struct
from pathlib import Path
from typing import Optional, Tuple
from gtts import gTTS
from backend.core.config import settings
from backend.core.logging import logger

class TTSService:
    """
    Text-to-Speech (TTS) Service.
    Generates synthesized speech for assistant replies with offline fallback.
    """

    def __init__(self):
        self.cache_dir = settings.audio_cache_dir

    def _generate_offline_wav(self, text: str, output_path: Path) -> Path:
        """
        Generates a valid, gentle ambient chime/tone WAV audio file for offline
        environments where external neural TTS endpoints cannot be reached.
        """
        sample_rate = 22050
        duration_s = min(max(len(text) // 25, 2), 6)  # 2 to 6 seconds proportional to text length
        num_samples = sample_rate * duration_s

        with wave.open(str(output_path), "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)

            # Generate gentle 432 Hz calming meditation frequency
            freq = 432.0
            frames = []
            for i in range(num_samples):
                # Gentle envelope fade-in and fade-out
                envelope = 1.0
                if i < sample_rate * 0.5:
                    envelope = i / (sample_rate * 0.5)
                elif i > num_samples - (sample_rate * 0.5):
                    envelope = (num_samples - i) / (sample_rate * 0.5)

                val = int(envelope * 10000.0 * math.sin(2.0 * math.pi * freq * (i / sample_rate)))
                frames.append(struct.pack("<h", val))

            wav_file.writeframes(b"".join(frames))
        return output_path

    async def synthesize_speech(self, text: str, lang: str = "en") -> Tuple[Path, str, str]:
        """
        Synthesizes text into spoken audio.
        Uses gTTS when online; falls back to ambient audio in offline/sandbox environments.
        Returns: (file_path: Path, mime_type: str, filename: str)
        """
        # Truncate very long texts for speech to avoid overwhelming audio files
        speech_text = text.strip()
        if len(speech_text) > 400:
            speech_text = speech_text[:397] + "..."

        file_id = uuid.uuid4().hex

        # Attempt online gTTS first
        mp3_path = self.cache_dir / f"{file_id}.mp3"
        try:
            tts = gTTS(text=speech_text, lang=lang, slow=False)
            tts.save(str(mp3_path))
            logger.info(f"Synthesized TTS audio using gTTS: {mp3_path.name}")
            return mp3_path, "audio/mpeg", mp3_path.name
        except Exception as exc:
            logger.info(f"gTTS online endpoint unavailable ({exc}). Using offline audio generator.")

        # Offline fallback: Generate calming WAV tone
        wav_path = self.cache_dir / f"{file_id}.wav"
        self._generate_offline_wav(speech_text, wav_path)
        logger.info(f"Generated offline fallback audio: {wav_path.name}")
        return wav_path, "audio/wav", wav_path.name

tts_service = TTSService()
