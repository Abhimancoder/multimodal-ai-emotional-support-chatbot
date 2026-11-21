from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from backend.core.config import settings
from backend.core.logging import logger
from backend.database.models import Base

# Determine Database Engine
engine = None
active_dialect = "unknown"

try:
    # Attempt MySQL connection
    mysql_engine = create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={"connect_timeout": 3}
    )
    # Test connection
    with mysql_engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    engine = mysql_engine
    active_dialect = "mysql"
    logger.info("Successfully connected to MySQL database.")
except Exception as exc:
    logger.warning(f"Could not connect to MySQL ({exc}).")
    if settings.USE_SQLITE_FALLBACK:
        sqlite_url = f"sqlite:///{settings.sqlite_full_path}"
        engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False}
        )
        active_dialect = "sqlite"
        logger.info(f"Fallen back to local SQLite database at: {settings.sqlite_full_path}")
    else:
        raise RuntimeError("MySQL connection failed and USE_SQLITE_FALLBACK is disabled.") from exc

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db() -> None:
    """Creates database tables if they do not already exist."""
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database schema initialized using [{active_dialect}].")

def get_db() -> Generator[Session, None, None]:
    """Dependency for providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def check_db_health() -> dict:
    """Checks database connectivity for the health check endpoint."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "dialect": active_dialect,
            "connected": True
        }
    except Exception as exc:
        return {
            "status": "degraded",
            "dialect": active_dialect,
            "connected": False,
            "error": str(exc)
        }
