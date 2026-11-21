import sys
from pathlib import Path

# Ensure project root is in sys.path so imports work regardless of launch directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st
from frontend.services.api_client import api_client
from frontend.components.disclaimer import render_disclaimer
from frontend.components.media_uploader import render_media_uploader
from frontend.components.grounding_card import render_grounding_card
from backend.services.emotional_support.grounding import GroundingService

# Configure Streamlit page
st.set_page_config(
    page_title="Mindful Companion - AI Emotional Support",
    page_icon="🌱",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Initialize Session State
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

def load_session_messages(session_id: str):
    """Loads historical messages from backend for the selected session."""
    st.session_state.current_session_id = session_id
    raw_msgs = api_client.get_session_messages(session_id)
    reconstructed = []
    for m in raw_msgs:
        item = {
            "role": m["role"],
            "content": m["content"],
            "modality": m.get("modality", "text"),
            "is_crisis": False
        }
        tts_path = m.get("tts_audio_path")
        if tts_path:
            item["audio_url"] = f"/audio/{Path(tts_path).name}"
        if m.get("has_grounding_card") and m.get("card_type"):
            item["grounding_card"] = GroundingService.get_exercise_details(m["card_type"])
        reconstructed.append(item)
    st.session_state.messages = reconstructed

# Sidebar: Sessions and System Status
with st.sidebar:
    st.header("🌱 Mindful Companion")
    
    # New Chat Button
    if st.button("➕ New Conversation", use_container_width=True, type="primary"):
        st.session_state.current_session_id = None
        st.session_state.messages = []
        st.rerun()

    st.subheader("💬 Conversations")
    sessions = api_client.list_sessions()
    if sessions:
        for s in sessions:
            label = s["title"]
            is_active = s["id"] == st.session_state.current_session_id
            
            col1, col2 = st.columns([0.85, 0.15])
            with col1:
                if st.button(label[:28], key=f"sess_{s['id']}", use_container_width=True):
                    load_session_messages(s["id"])
                    st.rerun()
            with col2:
                if st.button("🗑️", key=f"del_{s['id']}", help="Delete conversation"):
                    api_client.delete_session(s["id"])
                    if st.session_state.current_session_id == s["id"]:
                        st.session_state.current_session_id = None
                        st.session_state.messages = []
                    st.rerun()
    else:
        st.caption("No conversations yet.")

    st.divider()
    st.subheader("⚙️ System Status")
    health_info = api_client.get_health()
    status = health_info.get("status", "unknown")
    
    if status == "healthy":
        st.success("🟢 API: Connected")
        db_info = health_info.get("database", {})
        st.caption(f"Database: {db_info.get('dialect', 'N/A').upper()}")
        ai_info = health_info.get("ai_provider", {})
        if ai_info.get("configured"):
            st.caption(f"Model: {ai_info.get('model', 'N/A')}")
        else:
            st.warning("Model: Test/Dev Mode (Add key in .env)")
    else:
        st.error("🔴 API: Offline")
        st.caption("Run `uvicorn backend.main:app --reload`")

    st.divider()
    st.subheader("🔊 Output Preferences")
    enable_voice = st.checkbox(
        "Voice Audio Output (TTS)",
        value=False,
        help="When enabled, the companion generates voice audio playback for its responses."
    )

# App Header
st.title("🌱 Mindful Companion")
st.caption("A reflective, multimodal AI companion for emotional well-being and grounding.")

# Non-Clinical Transparency Disclaimer
render_disclaimer()

# Render Message Thread
if not st.session_state.messages:
    st.chat_message("assistant").write(
        "Hello! I am your Mindful Companion. I am here to listen, offer supportive thoughts, "
        "and share grounding techniques whenever you feel overwhelmed. You can type, upload a photo, or share a voice message. How are you feeling today?"
    )
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        is_crisis = msg.get("is_crisis", False)
        modality = msg.get("modality", "text")
        citations = msg.get("citations", [])
        card = msg.get("grounding_card")
        audio_url = msg.get("audio_url")
        
        with st.chat_message(role):
            if is_crisis:
                st.error("🚨 **Immediate Support & Crisis Resources:**")
            if modality != "text":
                st.caption(f"📎 Modality: {modality.title()}")
            st.write(content)
            
            # Render Voice Audio Player if TTS is present
            if audio_url:
                st.audio(api_client.get_full_audio_url(audio_url))

            # Render interactive grounding card if attached
            if card:
                render_grounding_card(card)
            
            # Render Verified Source Citations if present
            if citations:
                with st.expander("📚 Verified Coping Sources & References", expanded=False):
                    for cit in citations:
                        st.markdown(f"• **{cit.get('category', 'Wellness')}** — `{cit.get('source', '')}`")

# Media Attachments Widget
img_bytes, img_name, aud_bytes, aud_name = render_media_uploader(key_suffix=st.session_state.uploader_key)

# Action Row for sending when attachments are present without typing
has_attachments = bool(img_bytes or aud_bytes)

# Chat Input Box
user_prompt = st.chat_input("Share what is on your mind...")

send_triggered = False
message_text = None

if user_prompt:
    send_triggered = True
    message_text = user_prompt.strip()
elif has_attachments:
    if st.button("🚀 Send Attached Media", type="primary"):
        send_triggered = True
        message_text = None

if send_triggered:
    if message_text or has_attachments:
        if has_attachments:
            st.session_state.uploader_key += 1
        display_text = message_text or ("Sent attachment(s)" if has_attachments else "")
        # Add to message thread
        st.session_state.messages.append({
            "role": "user",
            "content": display_text,
            "modality": "multimodal" if (message_text and has_attachments) else ("image" if img_bytes else ("audio" if aud_bytes else "text"))
        })
        with st.chat_message("user"):
            st.write(display_text)

        # Call backend API
        with st.chat_message("assistant"):
            with st.spinner("Reflecting gently across your shared thoughts and media..."):
                response = api_client.send_message(
                    message=message_text,
                    session_id=st.session_state.current_session_id,
                    enable_audio=enable_voice,
                    image_bytes=img_bytes,
                    image_filename=img_name,
                    audio_bytes=aud_bytes,
                    audio_filename=aud_name
                )

            if response.get("success"):
                data = response["data"]
                st.session_state.current_session_id = data["session_id"]
                assistant_reply = data["assistant_message"]
                is_crisis = data.get("is_crisis", False)
                res_modality = data.get("modality", "text")

                if is_crisis:
                    st.error("🚨 **Immediate Support & Crisis Resources:**")
                st.write(assistant_reply)

                # Persist to UI state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_reply,
                    "modality": res_modality,
                    "is_crisis": is_crisis,
                    "audio_url": data.get("audio_url"),
                    "grounding_card": data.get("grounding_card"),
                    "citations": data.get("citations", [])
                })
                st.rerun()
            else:
                err_msg = response.get("error", "Failed to process multimodal message.")
                st.error(f"⚠️ {err_msg}")
