import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base Directory: root of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Current runtime environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    
    # Server Host & Ports
    BACKEND_HOST: str = Field(default="127.0.0.1", description="FastAPI bind host")
    BACKEND_PORT: int = Field(default=8000, description="FastAPI bind port")
    FRONTEND_PORT: int = Field(default=8501, description="Streamlit bind port")
    
    # Database Configuration
    DATABASE_URL: str = Field(
        default="mysql+pymysql://root:password@127.0.0.1:3306/emotional_support_db",
        description="MySQL connection URL"
    )
    USE_SQLITE_FALLBACK: bool = Field(
        default=True,
        description="Automatically fallback to SQLite if MySQL is unreachable during development"
    )
    SQLITE_DB_PATH: str = Field(
        default="storage/app.db",
        description="Local SQLite database file path for fallback mode"
    )
    
    # AI Provider
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API key")
    GEMINI_MODEL: str = Field(default="gemini-3.5-flash-lite", description="Model identifier")
    
    # ChromaDB
    CHROMA_PERSIST_DIR: str = Field(default="storage/chromadb", description="ChromaDB persistence directory")
    
    # File Upload Restrictions (bytes)
    MAX_IMAGE_SIZE_BYTES: int = Field(default=5 * 1024 * 1024, description="Max 5MB image")
    MAX_AUDIO_SIZE_BYTES: int = Field(default=10 * 1024 * 1024, description="Max 10MB audio")
    
    # Absolute Storage Directories
    @property
    def uploads_dir(self) -> Path:
        path = BASE_DIR / "storage" / "uploads"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def audio_cache_dir(self) -> Path:
        path = BASE_DIR / "storage" / "audio_cache"
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def sqlite_full_path(self) -> Path:
        path = BASE_DIR / self.SQLITE_DB_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Global settings instance
settings = Settings()
