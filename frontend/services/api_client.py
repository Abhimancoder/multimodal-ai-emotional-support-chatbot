import requests
from typing import Dict, Any, List, Optional, BinaryIO

class APIClient:
    """Client for communicating with the FastAPI backend."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def get_health(self) -> Dict[str, Any]:
        """Queries the /health endpoint of the backend."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            if response.status_code == 200:
                return response.json()
            return {
                "status": "degraded",
                "error": f"Status code {response.status_code}"
            }
        except requests.exceptions.RequestException as exc:
            return {
                "status": "unreachable",
                "error": f"Cannot connect to backend: {exc}"
            }

    def send_message(
        self,
        message: Optional[str] = None,
        session_id: Optional[str] = None,
        enable_audio: bool = False,
        image_bytes: Optional[bytes] = None,
        image_filename: Optional[str] = None,
        audio_bytes: Optional[bytes] = None,
        audio_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends a multimodal message (Text, Image, Audio) to the /chat endpoint.
        """
        data = {
            "enable_audio": "true" if enable_audio else "false"
        }
        if session_id:
            data["session_id"] = session_id
        if message:
            data["message"] = message

        files = {}
        if image_bytes and image_filename:
            files["image"] = (image_filename, image_bytes)
        if audio_bytes and audio_filename:
            files["audio"] = (audio_filename, audio_bytes)

        try:
            if files:
                response = requests.post(
                    f"{self.base_url}/chat",
                    data=data,
                    files=files,
                    timeout=60
                )
            else:
                response = requests.post(
                    f"{self.base_url}/chat",
                    json={
                        "message": message,
                        "session_id": session_id,
                        "enable_audio": enable_audio
                    },
                    timeout=60
                )

            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                try:
                    err_detail = response.json().get("detail", f"Server error ({response.status_code}).")
                except Exception:
                    err_detail = response.text or f"HTTP error ({response.status_code})."
                return {"success": False, "error": err_detail}
        except Exception as exc:
            return {"success": False, "error": f"Connection error: {exc}"}

    def get_full_audio_url(self, relative_path: str) -> str:
        """Constructs absolute URL for serving audio files."""
        if relative_path.startswith("http"):
            return relative_path
        return f"{self.base_url}/{relative_path.lstrip('/')}"

    def list_sessions(self) -> List[Dict[str, Any]]:
        """Retrieves active conversation sessions."""
        try:
            response = requests.get(f"{self.base_url}/sessions", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves messages for a session."""
        try:
            response = requests.get(f"{self.base_url}/sessions/{session_id}/messages", timeout=5)
            if response.status_code == 200:
                return response.json()
            return []
        except Exception:
            return []

    def delete_session(self, session_id: str) -> bool:
        """Deletes a conversation session."""
        try:
            response = requests.delete(f"{self.base_url}/sessions/{session_id}", timeout=5)
            return response.status_code == 204
        except Exception:
            return False

api_client = APIClient()
