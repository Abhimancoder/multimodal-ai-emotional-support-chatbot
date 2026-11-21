from fastapi import APIRouter
from backend.core.config import settings
from backend.schemas.health import HealthResponse, DatabaseHealth
from backend.database.connection import check_db_health

router = APIRouter(tags=["Health"])

@router.get("/health", response_model=HealthResponse)
async def get_system_health() -> HealthResponse:
    """Returns the operational status of the API, database, and configurations."""
    db_health_data = check_db_health()
    
    # Assess overall status
    is_healthy = db_health_data.get("connected", False)
    
    return HealthResponse(
        status="healthy" if is_healthy else "degraded",
        version="0.1.0",
        environment=settings.ENVIRONMENT,
        database=DatabaseHealth(
            status=db_health_data["status"],
            dialect=db_health_data["dialect"],
            connected=db_health_data["connected"],
            error=db_health_data.get("error")
        ),
        ai_provider={
            "provider": "google-gemini",
            "model": settings.GEMINI_MODEL,
            "configured": bool(settings.GEMINI_API_KEY)
        }
    )
