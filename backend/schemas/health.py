from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class DatabaseHealth(BaseModel):
    status: str
    dialect: str
    connected: bool
    error: Optional[str] = None

class HealthResponse(BaseModel):
    status: str = Field(..., json_schema_extra={"example": "healthy"})
    version: str = Field(..., json_schema_extra={"example": "0.1.0"})
    environment: str = Field(..., json_schema_extra={"example": "development"})
    database: DatabaseHealth
    ai_provider: Dict[str, Any]
