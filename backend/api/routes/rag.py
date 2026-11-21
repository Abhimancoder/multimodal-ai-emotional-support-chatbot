from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.database.connection import get_db
from backend.services.rag.retriever import rag_retriever

router = APIRouter(prefix="/rag", tags=["RAG"])

class IngestResponse(BaseModel):
    message: str
    total_chunks_indexed: int

class QueryRequest(BaseModel):
    query: str
    top_k: int = 3

class QueryResponse(BaseModel):
    query: str
    context_found: bool
    citations: List[Dict[str, str]]
    raw_context: str | None = None

@router.post("/ingest", response_model=IngestResponse)
async def ingest_knowledge_base(db: Session = Depends(get_db)) -> IngestResponse:
    """Ingests all documents from knowledge_base/ into ChromaDB and MySQL."""
    count = rag_retriever.ingest_all_documents(db=db)
    return IngestResponse(
        message="Knowledge base ingestion completed successfully.",
        total_chunks_indexed=count
    )

@router.post("/query", response_model=QueryResponse)
async def query_knowledge_base(payload: QueryRequest) -> QueryResponse:
    """Queries ChromaDB directly to inspect retrieved chunks and citations."""
    context, citations = rag_retriever.retrieve_context(
        query_text=payload.query,
        top_k=payload.top_k
    )
    return QueryResponse(
        query=payload.query,
        context_found=bool(context),
        citations=citations,
        raw_context=context
    )
