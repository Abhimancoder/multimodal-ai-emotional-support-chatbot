import streamlit as st

def render_disclaimer():
    """Renders the non-clinical transparent boundary banner."""
    st.info(
        "💡 **Important Disclaimer:** I am an AI emotional support companion, not a licensed therapist or healthcare professional. "
        "If you are facing an urgent crisis or immediate distress, please call/text **988** (Suicide & Crisis Lifeline) or reach out to local emergency services."
    )
