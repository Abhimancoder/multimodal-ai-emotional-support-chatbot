import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.rag.ingest import DocumentChunker
from backend.services.rag.retriever import rag_retriever

client = TestClient(app)

def test_document_chunker_basic():
    """Verify document cleaning and recursive character chunking."""
    sample_text = (
        "Box breathing is a 4-step technique.\n\n"
        "Step 1: Inhale for 4 seconds.\n"
        "Step 2: Hold for 4 seconds.\n"
        "Step 3: Exhale for 4 seconds.\n"
        "Step 4: Hold for 4 seconds."
    )
    chunks = DocumentChunker.chunk_text(sample_text, chunk_size=100, chunk_overlap=20)
    assert len(chunks) >= 1
    assert "Box breathing" in chunks[0]

def test_rag_ingest_and_query():
    """Verify knowledge base ingestion and semantic retrieval."""
    # 1. Ingest documents
    total_indexed = rag_retriever.ingest_all_documents()
    assert total_indexed > 0

    # 2. Query for box breathing
    context, citations = rag_retriever.retrieve_context("How do I practice box breathing?", top_k=2)
    assert context is not None
    assert "<retrieved_wellness_knowledge>" in context
    assert any("grounding_techniques.md" in c["source"] for c in citations)

def test_rag_query_healthy_communication():
    """Verify retrieval for communication and I-statements."""
    context, citations = rag_retriever.retrieve_context("How do I use I-statements with my roommate?", top_k=2)
    assert context is not None
    assert any("healthy_communication.md" in c["source"] for c in citations)

def test_rag_api_endpoints():
    """Verify /rag/ingest and /rag/query REST endpoints."""
    # Test Ingest endpoint
    ingest_resp = client.post("/rag/ingest")
    assert ingest_resp.status_code == 200
    assert ingest_resp.json()["total_chunks_indexed"] > 0

    # Test Query endpoint
    query_resp = client.post(
        "/rag/query",
        json={"query": "Tell me about cognitive reframing", "top_k": 2}
    )
    assert query_resp.status_code == 200
    data = query_resp.json()
    assert data["context_found"] is True
    assert any("stress_management.md" in c["source"] for c in data["citations"])

def test_chat_with_rag_citations():
    """Verify that chatting about grounding exercises returns verified citations."""
    response = client.post(
        "/chat",
        json={"message": "Can you explain the 5-4-3-2-1 grounding technique?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "citations" in data
    assert len(data["citations"]) > 0
    assert any("grounding_techniques.md" in c["source"] for c in data["citations"])
