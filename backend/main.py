from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.core.config import settings
from backend.core.logging import logger
from backend.database.connection import init_db, SessionLocal
from backend.services.rag.retriever import rag_retriever
from backend.api.routes import health, chat, sessions, rag, audio, maintenance

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: startup and shutdown."""
    logger.info("Initializing application resources...")
    try:
        init_db()
        logger.info("Database initialized successfully.")
        
        # Auto-ingest knowledge base documents into ChromaDB on startup
        db = SessionLocal()
        try:
            rag_retriever.ingest_all_documents(db=db)
        finally:
            db.close()
    except Exception as exc:
        logger.error(f"Failed to initialize database or knowledge base: {exc}")
    yield
    logger.info("Shutting down application resources.")

app = FastAPI(
    title="Multimodal Emotional Support Chatbot API",
    description="A secure, multimodal RAG-powered emotional support conversational assistant.",
    version="0.1.0",
    lifespan=lifespan
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Enforces essential HTTP security headers on all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# CORS Middleware (Allows Streamlit UI to communicate with FastAPI)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler (Never leak stack traces or internal secrets to client)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )

# Register routes
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(rag.router)
app.include_router(audio.router)
app.include_router(maintenance.router)

@app.get("/")
async def root():
    return {
        "message": "Multimodal Emotional Support Chatbot API is running.",
        "documentation": "/docs",
        "health": "/health"
    }
