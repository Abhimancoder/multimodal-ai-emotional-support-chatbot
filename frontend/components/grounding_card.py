import streamlit as st
from typing import Dict, Any

def render_grounding_card(card_data: Dict[str, Any]):
    """Renders a structured, visually calming exercise card in Streamlit."""
    title = card_data.get("title", "Grounding Exercise")
    category = card_data.get("category", "Mindfulness")
    purpose = card_data.get("purpose", "")
    steps = card_data.get("steps", [])

    st.markdown("---")
    with st.container():
        st.markdown(f"### 🧘 {title}")
        st.caption(f"**Focus:** {category} | {purpose}")

        if "box_breathing" in title.lower() or "breathing" in title.lower():
            cols = st.columns(len(steps) if steps else 1)
            for i, step in enumerate(steps):
                with cols[i]:
                    st.metric(
                        label=step.get("phase", f"Step {i+1}"),
                        value=f"{step.get('duration_seconds', 4)}s"
                    )
                    st.caption(step.get("instruction", ""))
        else:
            for s in steps:
                sense = s.get("sense", "Action")
                count = s.get("count", "")
                label = f"{count} {sense.upper()}" if count else sense
                st.markdown(f"• **{label}:** {s.get('instruction', '')}")
    st.markdown("---")
