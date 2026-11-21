from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAIProvider(ABC):
    """
    Abstract interface for AI model providers.
    Ensures that the model provider can be swapped (e.g., Gemini, OpenAI, Claude, local models)
    without rewriting application or API routes.
    """

    @abstractmethod
    async def generate_text_response(
        self,
        prompt: str,
        history: List[Dict[str, str]],
        system_instruction: str,
    ) -> str:
        """
        Generates an empathetic text response given the user prompt,
        prior conversation history, and system instruction.
        """
        pass

    @abstractmethod
    async def generate_multimodal_response(
        self,
        prompt: Optional[str],
        image_bytes: Optional[bytes],
        image_mime: Optional[str],
        audio_transcript: Optional[str],
        history: List[Dict[str, str]],
        system_instruction: str,
        rag_context: Optional[str] = None,
    ) -> str:
        """
        Generates a response from multimodal inputs and retrieved RAG context.
        """
        pass
