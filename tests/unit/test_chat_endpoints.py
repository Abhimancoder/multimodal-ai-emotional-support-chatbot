import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.database.connection import SessionLocal
from backend.database.models import ChatSession, Message

client = TestClient(app)

def test_chat_empty_message_rejected():
    """Verify that empty or whitespace messages are rejected with 400 Bad Request."""
    response = client.post("/chat", json={"message": "   "})
    assert response.status_code == 400
    assert "cannot be empty" in response.json()["detail"]

def test_chat_text_happy_path():
    """Verify successful text message submission and response generation."""
    response = client.post("/chat", json={"message": "Hello, I am feeling a little anxious today."})
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["user_message"] == "Hello, I am feeling a little anxious today."
    assert len(data["assistant_message"]) > 0
    assert data["is_crisis"] is False

    session_id = data["session_id"]

    # Verify turn 2: follow-up in the same session
    response2 = client.post(
        "/chat",
        json={
            "session_id": session_id,
            "message": "Can you give me one grounding exercise?"
        }
    )
    assert response2.status_code == 200
    data2 = response2.json()
    assert data2["session_id"] == session_id

def test_session_management():
    """Verify listing, message history, and deletion of sessions."""
    # Create a message to ensure session exists
    chat_resp = client.post("/chat", json={"message": "Testing session persistence"})
    assert chat_resp.status_code == 200
    session_id = chat_resp.json()["session_id"]

    # 1. List sessions
    list_resp = client.get("/sessions")
    assert list_resp.status_code == 200
    sessions = list_resp.json()
    assert any(s["id"] == session_id for s in sessions)

    # 2. Get session messages
    msg_resp = client.get(f"/sessions/{session_id}/messages")
    assert msg_resp.status_code == 200
    messages = msg_resp.json()
    assert len(messages) >= 2  # At least user + assistant turns

    # 3. Delete session
    del_resp = client.delete(f"/sessions/{session_id}")
    assert del_resp.status_code == 204

    # Verify session is deleted
    msg_resp2 = client.get(f"/sessions/{session_id}/messages")
    assert len(msg_resp2.json()) == 0

def test_chat_crisis_interception():
    """Verify that acute crisis triggers immediate 988 lifeline intervention."""
    response = client.post("/chat", json={"message": "I want to kill myself"})
    assert response.status_code == 200
    data = response.json()
    assert data["is_crisis"] is True
    assert "988" in data["assistant_message"]
    assert "Crisis Text Line" in data["assistant_message"]
